"""
Event Manager Service - Unified SSE and WebSocket event broadcasting

This service provides a centralized way to manage real-time event delivery
for prediction updates via both SSE and WebSocket connections.
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from weakref import WeakSet
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for real-time updates"""
    CONNECTION = "connection"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    PROGRESS = "progress"
    STATUS = "status"
    COMPLETED = "completed"
    FAILED = "failed"
    KEEPALIVE = "keepalive"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"


@dataclass
class PredictionEvent:
    """Represents an event for a prediction"""
    event_type: EventType
    response_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.event_type.value,
            "response_id": self.response_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_sse(self) -> Dict[str, str]:
        """Format for SSE response"""
        return {
            "event": self.event_type.value,
            "data": json.dumps(self.to_dict())
        }
    
    def to_json(self) -> str:
        """Format for WebSocket"""
        return json.dumps(self.to_dict())


class SSESubscription:
    """Manages an SSE connection subscription"""
    
    def __init__(self, response_id: str):
        self.response_id = response_id
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active = True
        self.created_at = datetime.utcnow()
        self.last_event_at = datetime.utcnow()
    
    async def put_event(self, event: PredictionEvent):
        """Put event in queue for delivery"""
        if self.active:
            await self.queue.put(event)
            self.last_event_at = datetime.utcnow()
    
    async def get_event(self, timeout: float = 30.0) -> Optional[PredictionEvent]:
        """Get next event with timeout"""
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    def close(self):
        """Close the subscription"""
        self.active = False


class WebSocketConnection:
    """Manages a WebSocket connection"""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.subscriptions: Set[str] = set()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active = True
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def subscribe(self, response_id: str):
        """Subscribe to a prediction's events"""
        self.subscriptions.add(response_id)
    
    def unsubscribe(self, response_id: str):
        """Unsubscribe from a prediction's events"""
        self.subscriptions.discard(response_id)
    
    def is_subscribed(self, response_id: str) -> bool:
        """Check if subscribed to a prediction"""
        return response_id in self.subscriptions
    
    async def send_event(self, event: PredictionEvent):
        """Send event to WebSocket"""
        if self.active and event.response_id in self.subscriptions:
            try:
                await self.websocket.send_text(event.to_json())
                self.last_activity = datetime.utcnow()
            except Exception as e:
                logger.warning(f"Failed to send WebSocket event: {e}")
                self.active = False
    
    async def send_json(self, data: Dict[str, Any]):
        """Send raw JSON to WebSocket"""
        if self.active:
            try:
                await self.websocket.send_json(data)
                self.last_activity = datetime.utcnow()
            except Exception as e:
                logger.warning(f"Failed to send WebSocket JSON: {e}")
                self.active = False
    
    def close(self):
        """Close the connection"""
        self.active = False
        self.subscriptions.clear()


class EventManager:
    """
    Unified event manager for SSE and WebSocket connections.
    
    Features:
    - Centralized event broadcasting
    - SSE subscription management
    - WebSocket connection management
    - Automatic cleanup of dead connections
    - Event history for late subscribers
    """
    
    def __init__(self, event_history_limit: int = 100):
        # SSE subscriptions: response_id -> list of subscriptions
        self._sse_subscriptions: Dict[str, List[SSESubscription]] = {}
        
        # WebSocket connections
        self._ws_connections: Set[WebSocketConnection] = set()
        
        # Event history per prediction (for late subscribers)
        self._event_history: Dict[str, List[PredictionEvent]] = {}
        self._event_history_limit = event_history_limit
        
        # Locks for thread safety
        self._sse_lock = asyncio.Lock()
        self._ws_lock = asyncio.Lock()
        
        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the event manager"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("EventManager started")
    
    async def stop(self):
        """Stop the event manager"""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all SSE subscriptions
        async with self._sse_lock:
            for subs in self._sse_subscriptions.values():
                for sub in subs:
                    sub.close()
            self._sse_subscriptions.clear()
        
        # Close all WebSocket connections
        async with self._ws_lock:
            for conn in self._ws_connections:
                conn.close()
            self._ws_connections.clear()
        
        logger.info("EventManager stopped")
    
    # ========================
    # SSE Management
    # ========================
    
    async def create_sse_subscription(self, response_id: str) -> SSESubscription:
        """Create a new SSE subscription for a prediction"""
        subscription = SSESubscription(response_id)
        
        async with self._sse_lock:
            if response_id not in self._sse_subscriptions:
                self._sse_subscriptions[response_id] = []
            self._sse_subscriptions[response_id].append(subscription)
        
        logger.debug(f"Created SSE subscription for {response_id}")
        return subscription
    
    async def remove_sse_subscription(self, subscription: SSESubscription):
        """Remove an SSE subscription"""
        subscription.close()
        
        async with self._sse_lock:
            response_id = subscription.response_id
            if response_id in self._sse_subscriptions:
                try:
                    self._sse_subscriptions[response_id].remove(subscription)
                    if not self._sse_subscriptions[response_id]:
                        del self._sse_subscriptions[response_id]
                except ValueError:
                    pass
        
        logger.debug(f"Removed SSE subscription for {subscription.response_id}")
    
    # ========================
    # WebSocket Management
    # ========================
    
    async def add_ws_connection(self, websocket: WebSocket) -> WebSocketConnection:
        """Add a new WebSocket connection"""
        await websocket.accept()
        connection = WebSocketConnection(websocket)
        
        async with self._ws_lock:
            self._ws_connections.add(connection)
        
        logger.debug(f"Added WebSocket connection, total: {len(self._ws_connections)}")
        return connection
    
    async def remove_ws_connection(self, connection: WebSocketConnection):
        """Remove a WebSocket connection"""
        connection.close()
        
        async with self._ws_lock:
            self._ws_connections.discard(connection)
        
        logger.debug(f"Removed WebSocket connection, remaining: {len(self._ws_connections)}")
    
    async def subscribe_ws(self, connection: WebSocketConnection, response_id: str):
        """Subscribe a WebSocket connection to a prediction's events"""
        connection.subscribe(response_id)
        
        # Send recent event history
        if response_id in self._event_history:
            for event in self._event_history[response_id][-5:]:  # Last 5 events
                await connection.send_event(event)
        
        await connection.send_json({
            "type": EventType.SUBSCRIBED.value,
            "response_id": response_id,
            "message": f"Subscribed to updates for {response_id}"
        })
        
        logger.debug(f"WebSocket subscribed to {response_id}")
    
    async def unsubscribe_ws(self, connection: WebSocketConnection, response_id: str):
        """Unsubscribe a WebSocket connection from a prediction's events"""
        connection.unsubscribe(response_id)
        
        await connection.send_json({
            "type": EventType.UNSUBSCRIBED.value,
            "response_id": response_id
        })
        
        logger.debug(f"WebSocket unsubscribed from {response_id}")
    
    # ========================
    # Event Broadcasting
    # ========================
    
    async def broadcast_event(
        self,
        response_id: str,
        event_type: EventType,
        data: Dict[str, Any]
    ):
        """Broadcast an event to all subscribers"""
        event = PredictionEvent(
            event_type=event_type,
            response_id=response_id,
            data=data
        )
        
        # Store in history
        if response_id not in self._event_history:
            self._event_history[response_id] = []
        self._event_history[response_id].append(event)
        
        # Trim history if needed
        if len(self._event_history[response_id]) > self._event_history_limit:
            self._event_history[response_id] = self._event_history[response_id][-self._event_history_limit:]
        
        # Broadcast to SSE subscribers
        await self._broadcast_to_sse(event)
        
        # Broadcast to WebSocket connections
        await self._broadcast_to_ws(event)
        
        logger.debug(f"Broadcast {event_type.value} event for {response_id}")
    
    async def _broadcast_to_sse(self, event: PredictionEvent):
        """Broadcast event to SSE subscribers"""
        async with self._sse_lock:
            subscriptions = self._sse_subscriptions.get(event.response_id, [])
            dead_subscriptions = []
            
            for sub in subscriptions:
                if sub.active:
                    try:
                        await asyncio.wait_for(sub.put_event(event), timeout=1.0)
                    except asyncio.TimeoutError:
                        dead_subscriptions.append(sub)
                else:
                    dead_subscriptions.append(sub)
            
            # Clean up dead subscriptions
            for sub in dead_subscriptions:
                try:
                    subscriptions.remove(sub)
                except ValueError:
                    pass
    
    async def _broadcast_to_ws(self, event: PredictionEvent):
        """Broadcast event to WebSocket connections"""
        async with self._ws_lock:
            dead_connections = []
            
            for conn in self._ws_connections:
                if conn.active and conn.is_subscribed(event.response_id):
                    try:
                        await conn.send_event(event)
                    except Exception:
                        dead_connections.append(conn)
                elif not conn.active:
                    dead_connections.append(conn)
            
            # Clean up dead connections
            for conn in dead_connections:
                self._ws_connections.discard(conn)
    
    # ========================
    # Convenience Methods
    # ========================
    
    async def emit_progress(self, response_id: str, progress: int, message: str):
        """Emit a progress event"""
        await self.broadcast_event(
            response_id,
            EventType.PROGRESS,
            {"progress": progress, "message": message}
        )
    
    async def emit_completed(self, response_id: str, result: Dict[str, Any]):
        """Emit a completed event"""
        await self.broadcast_event(
            response_id,
            EventType.COMPLETED,
            {"result": result}
        )
    
    async def emit_failed(self, response_id: str, error: str):
        """Emit a failed event"""
        await self.broadcast_event(
            response_id,
            EventType.FAILED,
            {"error": error}
        )
    
    async def emit_status(self, response_id: str, status: str, progress: int = 0):
        """Emit a status event"""
        await self.broadcast_event(
            response_id,
            EventType.STATUS,
            {"status": status, "progress": progress}
        )
    
    # ========================
    # Utility Methods
    # ========================
    
    def get_event_history(self, response_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent event history for a prediction"""
        events = self._event_history.get(response_id, [])
        return [e.to_dict() for e in events[-limit:]]
    
    def clear_event_history(self, response_id: str):
        """Clear event history for a prediction"""
        if response_id in self._event_history:
            del self._event_history[response_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "sse_subscriptions": sum(len(subs) for subs in self._sse_subscriptions.values()),
            "sse_predictions": len(self._sse_subscriptions),
            "ws_connections": len(self._ws_connections),
            "ws_subscriptions": sum(len(c.subscriptions) for c in self._ws_connections),
            "event_history_predictions": len(self._event_history),
            "total_events_in_history": sum(len(events) for events in self._event_history.values())
        }
    
    async def _cleanup_loop(self):
        """Background task to clean up stale connections"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Run every minute
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_stale_connections(self):
        """Clean up stale connections and old event history"""
        now = datetime.utcnow()
        stale_threshold = 300  # 5 minutes
        
        # Clean up stale SSE subscriptions
        async with self._sse_lock:
            for response_id, subs in list(self._sse_subscriptions.items()):
                stale = [
                    s for s in subs 
                    if not s.active or (now - s.last_event_at).total_seconds() > stale_threshold
                ]
                for sub in stale:
                    sub.close()
                    subs.remove(sub)
                if not subs:
                    del self._sse_subscriptions[response_id]
        
        # Clean up stale WebSocket connections
        async with self._ws_lock:
            stale_connections = [
                c for c in self._ws_connections
                if not c.active or (now - c.last_activity).total_seconds() > stale_threshold
            ]
            for conn in stale_connections:
                conn.close()
                self._ws_connections.discard(conn)
        
        # Clean up old event history (older than 1 hour)
        history_threshold = 3600
        for response_id, events in list(self._event_history.items()):
            if events:
                oldest = events[0].timestamp
                if (now - oldest).total_seconds() > history_threshold:
                    # Check if any active subscriptions
                    has_subscribers = (
                        response_id in self._sse_subscriptions or
                        any(conn.is_subscribed(response_id) for conn in self._ws_connections)
                    )
                    if not has_subscribers:
                        del self._event_history[response_id]


# Singleton instance
event_manager = EventManager()
