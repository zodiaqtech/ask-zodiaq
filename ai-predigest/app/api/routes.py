"""
API Routes for MyZodiaq Marriage API
With PostgreSQL storage, SSE, and WebSocket support
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import json
import logging

from app.models.schemas import (
    PredictRequest,
    PredictResponse,
    StatusResponse,
    ResultResponse,
    HealthResponse
)
from app.services.astro_engine import astro_engine
from app.services.db_service import db_service
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter()


# ========================
# Helper Functions
# ========================

def generate_response_id() -> str:
    """Generate unique response ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    return f"{timestamp}-{uuid4().hex[:8]}"


async def process_prediction_task(
    response_id: str,
    request: PredictRequest
):
    """Background task to process prediction"""
    try:
        # DEBUG: Log domain and subtopics
        print(f"🔍 [ROUTES DEBUG] domain='{request.domain}', subtopics={request.subtopic}")
        
        # Update status to processing
        await db_service.update_progress(response_id, 5, "Starting prediction...")
        
        # Create progress callback
        async def progress_callback(progress: int, message: str):
            await db_service.update_progress(response_id, progress, message)
        
        # Process the prediction
        result = await astro_engine.process_prediction(
            response_id=response_id,
            name=request.name,
            sex=request.sex,
            dob=request.dob,
            tob=request.tob,
            lat=request.lat,
            lon=request.lon,
            domain=request.domain,
            subtopics=request.subtopic,
            person2=request.person2.model_dump() if request.person2 else None,
            progress_callback=progress_callback,
            language=request.language,
            timezone=request.timezone if request.timezone is not None else 5.5
        )
        
        # Mark as completed
        await db_service.complete_prediction(response_id, result)
        
    except Exception as e:
        logger.exception(f"Prediction processing error for {response_id}")
        await db_service.fail_prediction(response_id, str(e))


# ========================
# Prediction Endpoints
# ========================

@router.post("/predict", response_model=PredictResponse)
async def create_prediction(
    request: PredictRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new prediction request.
    Returns immediately with response_id for tracking.
    """
    # Generate response ID immediately
    response_id = generate_response_id()
    
    try:
        # Create prediction record in database
        await db_service.create_prediction(
            response_id=response_id,
            name=request.name,
            sex=request.sex,
            dob=request.dob,
            tob=request.tob,
            lat=request.lat,
            lon=request.lon,
            domain=request.domain,
            subtopics=request.subtopic,
            person2_data=request.person2.model_dump() if request.person2 else None,
            language=request.language,
            timezone=f"UTC{'+' if (request.timezone or 5.5) >= 0 else ''}{request.timezone or 5.5}"
        )
        
        # Start background processing
        background_tasks.add_task(process_prediction_task, response_id, request)
        
        return PredictResponse(
            success=True,
            response_id=response_id,
            status="pending",
            message="Prediction request received. Use /status/{response_id} or /events/{response_id} to track progress."
        )
        
    except Exception as e:
        logger.exception(f"Failed to create prediction")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{response_id}", response_model=StatusResponse)
async def get_prediction_status(response_id: str):
    """
    Get current status and progress of a prediction.
    """
    status = await db_service.get_prediction_status(response_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return StatusResponse(
        success=True,
        response_id=status["response_id"],
        status=status["status"],
        progress=status["progress"],
        message=status.get("message", ""),  # message column doesn't exist in DB
        error_message=status.get("error_message")
    )


@router.get("/result/{response_id}", response_model=ResultResponse)
async def get_prediction_result(response_id: str):
    """
    Get the result of a completed prediction.
    """
    result = await db_service.get_prediction_result(response_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    if result["status"] == "pending" or result["status"] == "processing":
        raise HTTPException(
            status_code=202,
            detail={
                "status": result["status"],
                "message": "Prediction is still processing"
            }
        )
    
    if result["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": result.get("error_message", "Unknown error")
            }
        )
    
    return ResultResponse(
        success=True,
        response_id=result["response_id"],
        status=result["status"],
        result=result.get("result")
    )


@router.delete("/prediction/{response_id}")
async def delete_prediction(response_id: str):
    """Delete a prediction and its associated data."""
    deleted = await db_service.delete_prediction(response_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return {"success": True, "message": "Prediction deleted"}


@router.get("/predictions")
async def list_predictions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None
):
    """
    List predictions with optional filters.
    """
    predictions = await db_service.list_predictions(
        limit=limit,
        offset=offset,
        status=status
    )
    
    return {
        "predictions": predictions,
        "count": len(predictions),
        "limit": limit,
        "offset": offset
    }


@router.get("/events-history/{response_id}")
async def get_prediction_events(response_id: str, limit: int = Query(50, ge=1, le=200)):
    """
    Get historical events for a prediction.
    """
    # Check if prediction exists
    prediction = await db_service.get_prediction(response_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    events = await db_service.get_prediction_events(response_id, limit)
    
    return {
        "response_id": response_id,
        "events": events,
        "count": len(events)
    }


# ========================
# Server-Sent Events (SSE)
# ========================

@router.get("/events/{response_id}")
async def sse_events(response_id: str):
    """
    Server-Sent Events endpoint for real-time prediction updates.
    
    Event Types:
    - connection: Initial connection established
    - progress: Progress update with percentage and message
    - completed: Prediction completed with result
    - failed: Prediction failed with error
    """
    # Check if prediction exists
    prediction = await db_service.get_prediction(response_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    async def event_generator():
        # Send connection event
        yield {
            "event": "connection",
            "data": json.dumps({
                "type": "connected",
                "response_id": response_id,
                "current_status": prediction.status.value if prediction.status else "unknown",
                "current_progress": prediction.progress
            })
        }
        
        # If already completed or failed, send final event and close
        if prediction.status and prediction.status.value == "completed":
            yield {
                "event": "completed",
                "data": json.dumps({
                    "type": "completed",
                    "response_id": response_id,
                    "data": {"result": prediction.result}
                })
            }
            return
        
        if prediction.status and prediction.status.value == "failed":
            yield {
                "event": "failed",
                "data": json.dumps({
                    "type": "failed",
                    "response_id": response_id,
                    "data": {"error": prediction.error_message}
                })
            }
            return
        
        # Subscribe to updates
        queue = db_service.subscribe(response_id)
        
        try:
            while True:
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    event_type = event.get("type", "update")
                    
                    yield {
                        "event": event_type,
                        "data": json.dumps(event)
                    }
                    
                    # Close connection on terminal events
                    if event_type in ("completed", "failed"):
                        break
                        
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {
                        "event": "keepalive",
                        "data": json.dumps({"type": "keepalive", "timestamp": datetime.utcnow().isoformat()})
                    }
                    
        except asyncio.CancelledError:
            logger.debug(f"SSE connection cancelled for {response_id}")
        finally:
            db_service.unsubscribe(response_id, queue)
    
    return EventSourceResponse(event_generator())


# ========================
# WebSocket
# ========================

class WebSocketManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_subscriptions: Dict[WebSocket, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, response_id: Optional[str] = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.connection_subscriptions[websocket] = []
        
        if response_id:
            await self.subscribe(websocket, response_id)
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnect"""
        # Unsubscribe from all response_ids
        if websocket in self.connection_subscriptions:
            for response_id in self.connection_subscriptions[websocket]:
                if response_id in self.active_connections:
                    try:
                        self.active_connections[response_id].remove(websocket)
                        if not self.active_connections[response_id]:
                            del self.active_connections[response_id]
                    except ValueError:
                        pass
            del self.connection_subscriptions[websocket]
    
    async def subscribe(self, websocket: WebSocket, response_id: str):
        """Subscribe connection to a prediction"""
        if response_id not in self.active_connections:
            self.active_connections[response_id] = []
        
        if websocket not in self.active_connections[response_id]:
            self.active_connections[response_id].append(websocket)
            self.connection_subscriptions[websocket].append(response_id)
            
            await websocket.send_json({
                "type": "subscribed",
                "response_id": response_id,
                "message": f"Subscribed to updates for {response_id}"
            })
    
    async def unsubscribe(self, websocket: WebSocket, response_id: str):
        """Unsubscribe connection from a prediction"""
        if response_id in self.active_connections:
            try:
                self.active_connections[response_id].remove(websocket)
                if not self.active_connections[response_id]:
                    del self.active_connections[response_id]
            except ValueError:
                pass
        
        if websocket in self.connection_subscriptions:
            try:
                self.connection_subscriptions[websocket].remove(response_id)
            except ValueError:
                pass
        
        await websocket.send_json({
            "type": "unsubscribed",
            "response_id": response_id
        })
    
    async def broadcast(self, response_id: str, message: Dict[str, Any]):
        """Broadcast message to all connections subscribed to response_id"""
        if response_id not in self.active_connections:
            return
        
        dead_connections = []
        for connection in self.active_connections[response_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        
        # Clean up dead connections
        for conn in dead_connections:
            self.disconnect(conn)


ws_manager = WebSocketManager()


@router.websocket("/ws/{response_id}")
async def websocket_single(websocket: WebSocket, response_id: str):
    """
    WebSocket endpoint for a single prediction.
    Automatically subscribes to the specified response_id.
    """
    # Check if prediction exists
    prediction = await db_service.get_prediction(response_id)
    if not prediction:
        await websocket.close(code=4004, reason="Prediction not found")
        return
    
    await ws_manager.connect(websocket, response_id)
    
    # Send current status
    await websocket.send_json({
        "type": "status",
        "response_id": response_id,
        "data": {
            "status": prediction.status.value if prediction.status else "unknown",
            "progress": prediction.progress,
            "message": prediction.progress_message
        }
    })
    
    # If already completed, send result
    if prediction.status and prediction.status.value == "completed":
        await websocket.send_json({
            "type": "completed",
            "response_id": response_id,
            "data": {"result": prediction.result}
        })
    
    # Subscribe to db_service updates
    queue = db_service.subscribe(response_id)
    
    try:
        while True:
            try:
                # Wait for either a message from client or an update
                done, pending = await asyncio.wait(
                    [
                        asyncio.create_task(websocket.receive_json()),
                        asyncio.create_task(queue.get())
                    ],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in pending:
                    task.cancel()
                
                for task in done:
                    result = task.result()
                    
                    # Check if it's a client message or db update
                    if isinstance(result, dict) and "command" in result:
                        # Client command
                        command = result.get("command")
                        if command == "ping":
                            await websocket.send_json({"type": "pong"})
                    else:
                        # DB update event
                        await websocket.send_json({
                            "type": result.get("type", "update"),
                            "response_id": response_id,
                            "data": result.get("data", result)
                        })
                        
                        if result.get("type") in ("completed", "failed"):
                            await websocket.close()
                            return
                            
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        logger.debug(f"WebSocket disconnected for {response_id}")
    finally:
        db_service.unsubscribe(response_id, queue)
        ws_manager.disconnect(websocket)


@router.websocket("/ws")
async def websocket_multi(websocket: WebSocket):
    """
    WebSocket endpoint for multiple predictions.
    Clients can subscribe/unsubscribe to multiple response_ids.
    
    Commands:
    - {"command": "subscribe", "response_id": "..."}
    - {"command": "unsubscribe", "response_id": "..."}
    - {"command": "ping"}
    """
    await ws_manager.connect(websocket)
    
    subscribed_queues: Dict[str, asyncio.Queue] = {}
    
    try:
        while True:
            try:
                # Create tasks for client messages and all subscribed queues
                tasks = [asyncio.create_task(websocket.receive_json())]
                queue_tasks = {}
                
                for rid, queue in subscribed_queues.items():
                    task = asyncio.create_task(queue.get())
                    tasks.append(task)
                    queue_tasks[task] = rid
                
                done, pending = await asyncio.wait(
                    tasks,
                    timeout=30.0,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in pending:
                    task.cancel()
                
                if not done:
                    # Timeout - send keepalive
                    await websocket.send_json({"type": "ping"})
                    continue
                
                for task in done:
                    try:
                        result = task.result()
                    except asyncio.CancelledError:
                        continue
                    
                    if task in queue_tasks:
                        # DB update from subscribed queue
                        rid = queue_tasks[task]
                        await websocket.send_json({
                            "type": result.get("type", "update"),
                            "response_id": rid,
                            "data": result.get("data", result)
                        })
                        
                        if result.get("type") in ("completed", "failed"):
                            # Unsubscribe from completed/failed predictions
                            if rid in subscribed_queues:
                                db_service.unsubscribe(rid, subscribed_queues[rid])
                                del subscribed_queues[rid]
                    else:
                        # Client command
                        command = result.get("command")
                        
                        if command == "subscribe":
                            rid = result.get("response_id")
                            if rid and rid not in subscribed_queues:
                                # Check if prediction exists
                                pred = await db_service.get_prediction(rid)
                                if pred:
                                    queue = db_service.subscribe(rid)
                                    subscribed_queues[rid] = queue
                                    await websocket.send_json({
                                        "type": "subscribed",
                                        "response_id": rid,
                                        "data": {
                                            "status": pred.status.value if pred.status else "unknown",
                                            "progress": pred.progress
                                        }
                                    })
                                else:
                                    await websocket.send_json({
                                        "type": "error",
                                        "response_id": rid,
                                        "message": "Prediction not found"
                                    })
                        
                        elif command == "unsubscribe":
                            rid = result.get("response_id")
                            if rid and rid in subscribed_queues:
                                db_service.unsubscribe(rid, subscribed_queues[rid])
                                del subscribed_queues[rid]
                                await websocket.send_json({
                                    "type": "unsubscribed",
                                    "response_id": rid
                                })
                        
                        elif command == "ping":
                            await websocket.send_json({"type": "pong"})
                            
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        logger.debug("WebSocket multi disconnected")
    finally:
        # Cleanup all subscriptions
        for rid, queue in subscribed_queues.items():
            db_service.unsubscribe(rid, queue)
        ws_manager.disconnect(websocket)


# ========================
# Domain/Subtopic Info
# ========================

@router.get("/domains")
async def list_domains():
    """List all available domains and their subtopics."""
    from app.domains import get_all_domains_info, list_domain_names
    
    domains_info = get_all_domains_info()
    
    # Format for API response
    domains = {}
    for name, info in domains_info.items():
        domains[name] = {
            "display_name": info.get("display_name", name),
            "description": info.get("description", ""),
            "subtopics": list(info.get("subtopics", {}).keys()),
            "count": len(info.get("subtopics", {}))
        }
    
    return {
        "domains": domains,
        "available_domains": list_domain_names()
    }


@router.get("/domains/{domain}/subtopics")
async def get_domain_subtopics(domain: str):
    """Get available subtopics for a specific domain."""
    from app.domains import get_domain, get_domain_info, list_domain_names
    
    domain_obj = get_domain(domain)
    if not domain_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Domain '{domain}' not found. Available domains: {list_domain_names()}"
        )
    
    info = get_domain_info(domain)
    subtopics_info = info.get("subtopics", {})
    
    # Build detailed subtopic response
    subtopics = []
    aliases = {}
    for name, sub_info in subtopics_info.items():
        subtopics.append({
            "name": name,
            "display_name": sub_info.get("display_name", name),
            "description": sub_info.get("description", ""),
            "requires_person2": sub_info.get("requires_person2", False)
        })
        # Build aliases map
        for alias in sub_info.get("aliases", []):
            aliases[alias] = name
    
    return {
        "domain": domain,
        "display_name": info.get("display_name", domain),
        "description": info.get("description", ""),
        "subtopics": subtopics,
        "aliases": aliases,
        "note": "You can use either the exact subtopic name or any of its aliases"
    }


# ========================
# Health Check
# ========================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    db_status = "healthy"
    try:
        # Test database connection
        await db_service.list_predictions(limit=1)
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version="1.0.0",
        database=db_status
    )