"""
Real-time Event Routes - Enhanced SSE and WebSocket endpoints

Provides:
- SSE endpoint for server-sent events
- WebSocket endpoints for bi-directional communication
- Connection health monitoring
- Event history endpoints
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from sse_starlette.sse import EventSourceResponse

from app.services.event_manager import event_manager, EventType
from app.services.db_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["Real-time Events"])


# ========================
# Server-Sent Events (SSE)
# ========================

@router.get("/sse/{response_id}")
async def sse_stream(response_id: str):
    """
    Server-Sent Events endpoint for real-time prediction updates.
    
    Connect to this endpoint to receive push notifications when:
    - Progress updates occur
    - Prediction completes
    - Prediction fails
    
    Event Types:
    - connection: Initial connection established with current status
    - progress: Progress update with percentage and message
    - completed: Prediction completed successfully with result
    - failed: Prediction failed with error message
    - keepalive: Heartbeat to maintain connection (every 30s)
    
    Example:
    ```javascript
    const eventSource = new EventSource('/api/v1/realtime/sse/' + responseId);
    
    eventSource.addEventListener('progress', (event) => {
        const data = JSON.parse(event.data);
        console.log(`Progress: ${data.data.progress}% - ${data.data.message}`);
    });
    
    eventSource.addEventListener('completed', (event) => {
        const data = JSON.parse(event.data);
        console.log('Completed:', data.data.result);
        eventSource.close();
    });
    
    eventSource.addEventListener('failed', (event) => {
        const data = JSON.parse(event.data);
        console.error('Failed:', data.data.error);
        eventSource.close();
    });
    ```
    """
    # Verify prediction exists
    prediction = await db_service.get_prediction(response_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    async def event_generator():
        subscription = None
        
        try:
            # Create subscription
            subscription = await event_manager.create_sse_subscription(response_id)
            
            # Send connection event with current status
            status_val = prediction.status.value if prediction.status else "unknown"
            yield {
                "event": EventType.CONNECTION.value,
                "data": json.dumps({
                    "type": "connected",
                    "response_id": response_id,
                    "current_status": status_val,
                    "current_progress": prediction.progress or 0,
                    "timestamp": datetime.utcnow().isoformat()
                })
            }
            
            # If already terminal, send final event and close
            if status_val == "completed":
                yield {
                    "event": EventType.COMPLETED.value,
                    "data": json.dumps({
                        "type": "completed",
                        "response_id": response_id,
                        "data": {"result": prediction.result},
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }
                return
            
            if status_val == "failed":
                yield {
                    "event": EventType.FAILED.value,
                    "data": json.dumps({
                        "type": "failed",
                        "response_id": response_id,
                        "data": {"error": prediction.error_message},
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }
                return
            
            # Stream events until completion/failure
            while subscription.active:
                event = await subscription.get_event(timeout=30.0)
                
                if event is None:
                    # Send keepalive
                    yield {
                        "event": EventType.KEEPALIVE.value,
                        "data": json.dumps({
                            "type": "keepalive",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    }
                    continue
                
                # Send the event
                yield event.to_sse()
                
                # Close on terminal events
                if event.event_type in (EventType.COMPLETED, EventType.FAILED):
                    break
                    
        except asyncio.CancelledError:
            logger.debug(f"SSE connection cancelled for {response_id}")
        finally:
            if subscription:
                await event_manager.remove_sse_subscription(subscription)
    
    return EventSourceResponse(event_generator())


# ========================
# WebSocket Endpoints
# ========================

@router.websocket("/ws/{response_id}")
async def websocket_single(websocket: WebSocket, response_id: str):
    """
    WebSocket endpoint for a single prediction.
    
    Automatically subscribes to the specified response_id on connect.
    
    Server Messages:
    - {"type": "status", "response_id": "...", "data": {...}}
    - {"type": "progress", "response_id": "...", "data": {...}}
    - {"type": "completed", "response_id": "...", "data": {...}}
    - {"type": "failed", "response_id": "...", "data": {...}}
    - {"type": "ping"}
    
    Client Commands:
    - {"command": "ping"} -> Responds with {"type": "pong"}
    """
    # Verify prediction exists
    prediction = await db_service.get_prediction(response_id)
    if not prediction:
        await websocket.close(code=4004, reason="Prediction not found")
        return
    
    connection = None
    
    try:
        # Accept and setup connection
        connection = await event_manager.add_ws_connection(websocket)
        await event_manager.subscribe_ws(connection, response_id)
        
        # Send current status
        status_val = prediction.status.value if prediction.status else "unknown"
        await connection.send_json({
            "type": EventType.STATUS.value,
            "response_id": response_id,
            "data": {
                "status": status_val,
                "progress": prediction.progress or 0,
                "message": "Connected to prediction updates"
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # If already completed, send result
        if status_val == "completed" and prediction.result:
            await connection.send_json({
                "type": EventType.COMPLETED.value,
                "response_id": response_id,
                "data": {"result": prediction.result},
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Handle client messages
        while connection.active:
            try:
                # Wait for client message with timeout
                message = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0
                )
                
                command = message.get("command")
                
                if command == "ping":
                    await connection.send_json({"type": EventType.PONG.value})
                elif command == "status":
                    # Re-fetch current status
                    current = await db_service.get_prediction_status(response_id)
                    if current:
                        await connection.send_json({
                            "type": EventType.STATUS.value,
                            "response_id": response_id,
                            "data": current,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        
            except asyncio.TimeoutError:
                # Send keepalive ping
                await connection.send_json({"type": EventType.PING.value})
                
    except WebSocketDisconnect:
        logger.debug(f"WebSocket disconnected for {response_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {response_id}: {e}")
    finally:
        if connection:
            await event_manager.remove_ws_connection(connection)


@router.websocket("/ws")
async def websocket_multi(websocket: WebSocket):
    """
    WebSocket endpoint for multiple predictions.
    
    Clients can subscribe/unsubscribe to multiple predictions dynamically.
    
    Client Commands:
    - {"command": "subscribe", "response_id": "..."}
    - {"command": "unsubscribe", "response_id": "..."}
    - {"command": "status", "response_id": "..."} - Get current status
    - {"command": "ping"} -> Responds with {"type": "pong"}
    - {"command": "list_subscriptions"} -> Lists active subscriptions
    
    Server Messages:
    - {"type": "subscribed", "response_id": "...", "data": {...}}
    - {"type": "unsubscribed", "response_id": "..."}
    - {"type": "progress", "response_id": "...", "data": {...}}
    - {"type": "completed", "response_id": "...", "data": {...}}
    - {"type": "failed", "response_id": "...", "data": {...}}
    - {"type": "error", "message": "..."}
    - {"type": "ping"}
    """
    connection = None
    
    try:
        connection = await event_manager.add_ws_connection(websocket)
        
        # Send connection confirmation
        await connection.send_json({
            "type": EventType.CONNECTION.value,
            "message": "Connected to multi-prediction WebSocket",
            "commands": ["subscribe", "unsubscribe", "status", "ping", "list_subscriptions"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while connection.active:
            try:
                message = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0
                )
                
                command = message.get("command")
                response_id = message.get("response_id")
                
                if command == "subscribe" and response_id:
                    # Verify prediction exists
                    prediction = await db_service.get_prediction(response_id)
                    if prediction:
                        await event_manager.subscribe_ws(connection, response_id)
                        # Send current status
                        status_val = prediction.status.value if prediction.status else "unknown"
                        await connection.send_json({
                            "type": EventType.STATUS.value,
                            "response_id": response_id,
                            "data": {
                                "status": status_val,
                                "progress": prediction.progress or 0
                            }
                        })
                    else:
                        await connection.send_json({
                            "type": EventType.ERROR.value,
                            "response_id": response_id,
                            "message": "Prediction not found"
                        })
                
                elif command == "unsubscribe" and response_id:
                    await event_manager.unsubscribe_ws(connection, response_id)
                
                elif command == "status" and response_id:
                    status = await db_service.get_prediction_status(response_id)
                    if status:
                        await connection.send_json({
                            "type": EventType.STATUS.value,
                            "response_id": response_id,
                            "data": status,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        await connection.send_json({
                            "type": EventType.ERROR.value,
                            "response_id": response_id,
                            "message": "Prediction not found"
                        })
                
                elif command == "ping":
                    await connection.send_json({"type": EventType.PONG.value})
                
                elif command == "list_subscriptions":
                    await connection.send_json({
                        "type": "subscriptions",
                        "data": list(connection.subscriptions)
                    })
                
                else:
                    await connection.send_json({
                        "type": EventType.ERROR.value,
                        "message": f"Unknown command: {command}"
                    })
                    
            except asyncio.TimeoutError:
                await connection.send_json({"type": EventType.PING.value})
                
    except WebSocketDisconnect:
        logger.debug("Multi-prediction WebSocket disconnected")
    except Exception as e:
        logger.error(f"Multi-prediction WebSocket error: {e}")
    finally:
        if connection:
            await event_manager.remove_ws_connection(connection)


# ========================
# Utility Endpoints
# ========================

@router.get("/events/{response_id}/history")
async def get_event_history(
    response_id: str,
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get recent event history for a prediction.
    
    Useful for clients that connect late and want to see recent events.
    """
    prediction = await db_service.get_prediction(response_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    history = event_manager.get_event_history(response_id, limit)
    
    return {
        "response_id": response_id,
        "events": history,
        "count": len(history)
    }


@router.get("/stats")
async def get_connection_stats():
    """
    Get real-time connection statistics.
    
    Useful for monitoring active connections and event delivery health.
    """
    return {
        "stats": event_manager.get_stats(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/test/{response_id}/progress")
async def test_emit_progress(
    response_id: str,
    progress: int = Query(50, ge=0, le=100),
    message: str = Query("Test progress message")
):
    """
    Test endpoint to emit a progress event.
    
    Useful for testing SSE/WebSocket connections.
    Only available in debug mode.
    """
    from config import get_settings
    settings = get_settings()
    
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Only available in debug mode")
    
    prediction = await db_service.get_prediction(response_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    await event_manager.emit_progress(response_id, progress, message)
    
    return {
        "success": True,
        "message": f"Emitted progress event: {progress}% - {message}"
    }
