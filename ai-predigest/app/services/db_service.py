"""
Database Service - PostgreSQL operations for predictions

Integrates with EventManager for real-time SSE/WebSocket broadcasting.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_
from sqlalchemy.orm import selectinload

from app.models.database import Base, Prediction, PredictionEvent, PredictionStatus
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class DatabaseService:
    """Async PostgreSQL database service"""
    
    def __init__(self):
        self.engine = None
        self.async_session_factory = None
        self._initialized = False
        
        # Event subscribers for real-time updates
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        import ssl as ssl_module
        
        if self._initialized:
            return
        
        database_url = settings.DATABASE_URL
        if not database_url:
            raise ValueError("DATABASE_URL is not configured")
        
        # Convert postgres:// to postgresql+asyncpg://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgresql://") and "asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Check if SSL is needed (Azure PostgreSQL requires it)
        needs_ssl = "ssl=" in database_url or "sslmode=" in database_url or "azure" in database_url.lower()
        
        # Remove ssl/sslmode from URL - we'll pass it via connect_args
        import re
        database_url = re.sub(r'[?&]ssl(mode)?=[^&]*', '', database_url)
        # Clean up any trailing ? or &&
        database_url = database_url.rstrip('?').replace('?&', '?').replace('&&', '&')
        
        logger.info(f"Connecting to database (SSL: {needs_ssl})...")
        
        # Configure SSL for Azure PostgreSQL
        connect_args = {}
        if needs_ssl:
            # Create SSL context for Azure PostgreSQL
            ssl_context = ssl_module.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl_module.CERT_NONE
            connect_args["ssl"] = ssl_context
        
        self.engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self._initialized = True
        logger.info("Database initialized successfully")
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    # ========================
    # Prediction CRUD
    # ========================
    
    async def create_prediction(
        self,
        response_id: str,
        name: str,
        sex: str,
        dob: str,
        tob: str,
        lat: float,
        lon: float,
        domain: str,
        subtopics: List[str],
        person2_data: Optional[Dict] = None,
        input_id: Optional[str] = None,
        timezone: str = "UTC+5:30",
        source: str = "api",
        questions: Optional[List] = None,
        language: str = "Hindi"
    ) -> Prediction:
        """Create a new prediction record
        
        Note: language is not stored in DB but is passed through for logging purposes.
        The language preference is included in the result output.
        """
        async with self.get_session() as session:
            prediction = Prediction(
                response_id=response_id,
                input_id=input_id or response_id,
                name=name,
                sex=sex,
                dob=dob,
                tob=tob,
                lat=float(lat),  # DB expects double precision
                lon=float(lon),  # DB expects double precision
                timezone=timezone,
                domain=domain,
                subtopic=",".join(subtopics) if isinstance(subtopics, list) else subtopics,  # DB expects VARCHAR
                questions=questions or [],  # NOT NULL in DB - default to empty list
                source=source,
                # Set individual person2 columns
                person2_name=person2_data.get("name") if person2_data else None,
                person2_sex=person2_data.get("sex") if person2_data else None,
                person2_dob=person2_data.get("dob") if person2_data else None,
                person2_tob=person2_data.get("tob") if person2_data else None,
                person2_lat=float(person2_data.get("lat")) if person2_data and person2_data.get("lat") else None,
                person2_lon=float(person2_data.get("lon")) if person2_data and person2_data.get("lon") else None,
                person2_timezone=(lambda tz: f"UTC{'+' if tz >= 0 else ''}{tz}")(person2_data.get("timezone") or 5.5) if person2_data else None,
                status=PredictionStatus.PENDING,
                progress=0,
                created_at=datetime.utcnow()
            )
            session.add(prediction)
            await session.flush()
            
            # TODO: Event logging disabled - prediction_events table has different schema
            # event = PredictionEvent(
            #     response_id=response_id,
            #     event_type="created",
            #     event_data={"status": "pending", "message": "Prediction request created"}
            # )
            # session.add(event)
            
            await session.commit()
            
            # Notify subscribers
            await self._notify_subscribers(response_id, {
                "type": "created",
                "response_id": response_id,
                "data": {"status": "pending", "message": "Prediction request created"}
            })
            
            return prediction
    
    async def get_prediction(self, response_id: str) -> Optional[Prediction]:
        """Get prediction by response_id"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Prediction).where(Prediction.response_id == response_id)
            )
            return result.scalar_one_or_none()
    
    async def update_progress(
        self, 
        response_id: str, 
        progress: int, 
        message: str
    ) -> bool:
        """Update prediction progress"""
        async with self.get_session() as session:
            result = await session.execute(
                update(Prediction)
                .where(Prediction.response_id == response_id)
                .values(
                    progress=progress,
                    status=PredictionStatus.PROCESSING,
                    updated_at=datetime.utcnow()
                )
            )
            
            if result.rowcount > 0:
                # TODO: Event logging disabled - prediction_events table has different schema
                await session.commit()
                
                # Notify subscribers
                await self._notify_subscribers(response_id, {
                    "type": "progress",
                    "response_id": response_id,
                    "data": {"progress": progress, "message": message}
                })
                
                return True
            return False
    
    async def complete_prediction(
        self, 
        response_id: str, 
        result: Dict[str, Any]
    ) -> bool:
        """Mark prediction as completed with result"""
        async with self.get_session() as session:
            now = datetime.utcnow()
            update_result = await session.execute(
                update(Prediction)
                .where(Prediction.response_id == response_id)
                .values(
                    status=PredictionStatus.COMPLETED,
                    progress=100,
                    result=result,
                    updated_at=now,
                    completed_at=now
                )
            )
            
            if update_result.rowcount > 0:
                # TODO: Event logging disabled - prediction_events table has different schema
                await session.commit()
                
                # Notify subscribers with result
                await self._notify_subscribers(response_id, {
                    "type": "completed",
                    "response_id": response_id,
                    "data": {"result": result}
                })
                
                return True
            return False
    
    async def fail_prediction(
        self, 
        response_id: str, 
        error_message: str
    ) -> bool:
        """Mark prediction as failed"""
        async with self.get_session() as session:
            result = await session.execute(
                update(Prediction)
                .where(Prediction.response_id == response_id)
                .values(
                    status=PredictionStatus.FAILED,
                    error_message=error_message,
                    updated_at=datetime.utcnow()
                )
            )
            
            if result.rowcount > 0:
                # TODO: Event logging disabled - prediction_events table has different schema
                await session.commit()
                
                # Notify subscribers
                await self._notify_subscribers(response_id, {
                    "type": "failed",
                    "response_id": response_id,
                    "data": {"error": error_message}
                })
                
                return True
            return False
    
    async def get_prediction_status(self, response_id: str) -> Optional[Dict[str, Any]]:
        """Get prediction status"""
        prediction = await self.get_prediction(response_id)
        if not prediction:
            return None
        
        # Generate dynamic message based on progress/status
        status_val = prediction.status.value if prediction.status else None
        progress = prediction.progress or 0
        
        if status_val == "completed":
            message = "Prediction completed successfully"
        elif status_val == "failed":
            message = "Prediction failed"
        elif status_val == "pending":
            message = "Request received, waiting to process"
        elif status_val == "processing":
            if progress < 10:
                message = "Initializing prediction engine..."
            elif progress < 25:
                message = "Fetching birth chart data..."
            elif progress < 40:
                message = "Calculating planetary positions..."
            elif progress < 55:
                message = "Analyzing house significators..."
            elif progress < 70:
                message = "Evaluating dasha periods..."
            elif progress < 85:
                message = "Generating AI predictions..."
            else:
                message = "Finalizing results..."
        else:
            message = "Processing..."
        
        return {
            "response_id": prediction.response_id,
            "status": status_val,
            "progress": progress,
            "message": message,
            "error_message": prediction.error_message,
            "created_at": prediction.created_at.isoformat() if prediction.created_at else None,
            "updated_at": prediction.updated_at.isoformat() if prediction.updated_at else None
        }
    
    async def get_prediction_result(self, response_id: str) -> Optional[Dict[str, Any]]:
        """Get prediction result"""
        prediction = await self.get_prediction(response_id)
        if not prediction:
            return None
        
        return {
            "response_id": prediction.response_id,
            "status": prediction.status.value if prediction.status else None,
            "result": prediction.result,
            "error_message": prediction.error_message
        }
    
    async def delete_prediction(self, response_id: str) -> bool:
        """Delete prediction and its events"""
        async with self.get_session() as session:
            # TODO: Event deletion disabled - prediction_events table has different schema
            # await session.execute(
            #     delete(PredictionEvent).where(PredictionEvent.response_id == response_id)
            # )
            
            # Delete prediction
            result = await session.execute(
                delete(Prediction).where(Prediction.response_id == response_id)
            )
            
            await session.commit()
            return result.rowcount > 0
    
    async def list_predictions(
        self, 
        limit: int = 10, 
        status: Optional[str] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List predictions with optional status filter"""
        async with self.get_session() as session:
            query = select(Prediction).order_by(Prediction.created_at.desc())
            
            if status:
                try:
                    status_enum = PredictionStatus(status)
                    query = query.where(Prediction.status == status_enum)
                except ValueError:
                    pass
            
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            predictions = result.scalars().all()
            
            return [
                {
                    "response_id": p.response_id,
                    "name": p.name,
                    "domain": p.domain,
                    "status": p.status.value if p.status else None,
                    "progress": p.progress,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in predictions
            ]
    
    # ========================
    # Event History
    # ========================
    
    async def get_prediction_events(
        self, 
        response_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get event history for a prediction"""
        # TODO: Disabled - prediction_events table has different schema
        return []
    
    # ========================
    # Real-time Subscriptions
    # ========================
    
    def subscribe(self, response_id: str) -> asyncio.Queue:
        """Subscribe to prediction updates"""
        if response_id not in self._subscribers:
            self._subscribers[response_id] = []
        
        queue = asyncio.Queue()
        self._subscribers[response_id].append(queue)
        logger.debug(f"New subscriber for {response_id}, total: {len(self._subscribers[response_id])}")
        return queue
    
    def unsubscribe(self, response_id: str, queue: asyncio.Queue):
        """Unsubscribe from prediction updates"""
        if response_id in self._subscribers:
            try:
                self._subscribers[response_id].remove(queue)
                if not self._subscribers[response_id]:
                    del self._subscribers[response_id]
                logger.debug(f"Unsubscribed from {response_id}")
            except ValueError:
                pass
    
    async def _notify_subscribers(self, response_id: str, event: Dict[str, Any]):
        """Notify all subscribers of an event (both local queues and event_manager)"""
        # Notify local queue subscribers (legacy support)
        if response_id in self._subscribers:
            dead_queues = []
            for queue in self._subscribers[response_id]:
                try:
                    await asyncio.wait_for(queue.put(event), timeout=1.0)
                except asyncio.TimeoutError:
                    dead_queues.append(queue)
                except Exception as e:
                    logger.warning(f"Failed to notify subscriber: {e}")
                    dead_queues.append(queue)
            
            # Clean up dead queues
            for queue in dead_queues:
                self.unsubscribe(response_id, queue)
        
        # Also broadcast via EventManager for SSE/WebSocket
        try:
            from app.services.event_manager import event_manager, EventType
            
            event_type_str = event.get("type", "update")
            event_type_map = {
                "created": EventType.STATUS,
                "progress": EventType.PROGRESS,
                "completed": EventType.COMPLETED,
                "failed": EventType.FAILED,
                "status": EventType.STATUS,
            }
            event_type = event_type_map.get(event_type_str, EventType.PROGRESS)
            
            await event_manager.broadcast_event(
                response_id=response_id,
                event_type=event_type,
                data=event.get("data", event)
            )
        except ImportError:
            pass  # event_manager not available
        except Exception as e:
            logger.warning(f"Failed to broadcast via event_manager: {e}")


# Singleton instance
db_service = DatabaseService()
