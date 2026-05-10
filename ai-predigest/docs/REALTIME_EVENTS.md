# Real-time Event System for MyZodiaq API

This document describes how to use the SSE (Server-Sent Events) and WebSocket endpoints for real-time prediction updates.

## Overview

Instead of polling the `/status/{response_id}` endpoint repeatedly, you can now receive push notifications when:
- Progress updates occur during prediction processing
- The prediction completes successfully
- The prediction fails

## Available Endpoints

| Endpoint | Type | Use Case |
|----------|------|----------|
| `/api/v1/realtime/sse/{response_id}` | SSE | Track a single prediction |
| `/api/v1/realtime/ws/{response_id}` | WebSocket | Track a single prediction with bi-directional communication |
| `/api/v1/realtime/ws` | WebSocket | Track multiple predictions simultaneously |
| `/api/v1/realtime/events/{response_id}/history` | REST | Get recent event history |
| `/api/v1/realtime/stats` | REST | Get connection statistics |

## Choosing Between SSE and WebSocket

### Use SSE when:
- You only need to track one prediction at a time
- You want simpler client code
- You don't need to send commands to the server
- You want automatic reconnection (built into browsers)

### Use WebSocket when:
- You need to track multiple predictions simultaneously
- You want bi-directional communication
- You need fine-grained control over subscriptions
- You're building a dashboard with many concurrent predictions

## Event Types

All real-time channels send these event types:

| Event Type | Description | Data |
|------------|-------------|------|
| `connection` | Initial connection established | `{current_status, current_progress}` |
| `progress` | Processing progress update | `{progress: number, message: string}` |
| `completed` | Prediction finished successfully | `{result: object}` |
| `failed` | Prediction encountered an error | `{error: string}` |
| `keepalive` | Connection health check | `{timestamp}` |

## SSE Usage

### JavaScript (Browser)

```javascript
// Start the prediction
const response = await fetch('/api/v1/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'John Doe',
    sex: 'male',
    dob: '15/05/1990',
    tob: '10:30',
    lat: 28.6139,
    lon: 77.2090,
    domain: 'Marriage',
    subtopic: ['Marriage Prospects']
  })
});

const { response_id } = await response.json();

// Connect to SSE
const eventSource = new EventSource(`/api/v1/realtime/sse/${response_id}`);

// Handle connection
eventSource.addEventListener('connection', (event) => {
  const data = JSON.parse(event.data);
  console.log('Connected!', data.current_status, data.current_progress);
});

// Handle progress updates
eventSource.addEventListener('progress', (event) => {
  const data = JSON.parse(event.data);
  const { progress, message } = data.data;
  updateProgressBar(progress);
  updateStatusText(message);
});

// Handle completion
eventSource.addEventListener('completed', (event) => {
  const data = JSON.parse(event.data);
  displayResult(data.data.result);
  eventSource.close();
});

// Handle failure
eventSource.addEventListener('failed', (event) => {
  const data = JSON.parse(event.data);
  showError(data.data.error);
  eventSource.close();
});

// Handle errors
eventSource.onerror = (error) => {
  console.error('SSE Error:', error);
  // Browser will automatically try to reconnect
};
```

### Python

```python
import requests
import sseclient

# Start prediction
response = requests.post('http://localhost:8000/api/v1/predict', json={
    'name': 'John Doe',
    'sex': 'male',
    'dob': '15/05/1990',
    'tob': '10:30',
    'lat': 28.6139,
    'lon': 77.2090,
    'domain': 'Marriage',
    'subtopic': ['Marriage Prospects']
})
response_id = response.json()['response_id']

# Connect to SSE
response = requests.get(
    f'http://localhost:8000/api/v1/realtime/sse/{response_id}',
    stream=True
)
client = sseclient.SSEClient(response)

for event in client.events():
    print(f'Event: {event.event}')
    print(f'Data: {event.data}')
    
    if event.event in ('completed', 'failed'):
        break
```

## WebSocket Usage

### Single Prediction

```javascript
// Connect to single prediction WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/v1/realtime/ws/${response_id}`);

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'status':
      console.log(`Status: ${data.data.status}, Progress: ${data.data.progress}`);
      break;
    case 'progress':
      console.log(`Progress: ${data.data.progress}% - ${data.data.message}`);
      break;
    case 'completed':
      console.log('Completed!', data.data.result);
      ws.close();
      break;
    case 'failed':
      console.error('Failed:', data.data.error);
      ws.close();
      break;
    case 'ping':
      // Server is checking connection, respond with pong
      ws.send(JSON.stringify({ command: 'ping' }));
      break;
  }
};

// Send ping to check connection
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ command: 'ping' }));
  }
}, 30000);
```

### Multiple Predictions

```javascript
// Connect to multi-prediction WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws');

ws.onopen = () => {
  console.log('Connected to multi-prediction WebSocket');
  
  // Subscribe to multiple predictions
  ws.send(JSON.stringify({ command: 'subscribe', response_id: 'pred-123' }));
  ws.send(JSON.stringify({ command: 'subscribe', response_id: 'pred-456' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'subscribed':
      console.log(`Subscribed to ${data.response_id}`);
      break;
    case 'unsubscribed':
      console.log(`Unsubscribed from ${data.response_id}`);
      break;
    case 'progress':
      console.log(`[${data.response_id}] Progress: ${data.data.progress}%`);
      break;
    case 'completed':
      console.log(`[${data.response_id}] Completed!`);
      break;
    case 'failed':
      console.error(`[${data.response_id}] Failed:`, data.data.error);
      break;
  }
};

// Available commands
// Subscribe to a prediction
ws.send(JSON.stringify({ command: 'subscribe', response_id: 'new-pred-id' }));

// Unsubscribe from a prediction
ws.send(JSON.stringify({ command: 'unsubscribe', response_id: 'pred-123' }));

// Get current status
ws.send(JSON.stringify({ command: 'status', response_id: 'pred-123' }));

// List subscriptions
ws.send(JSON.stringify({ command: 'list_subscriptions' }));

// Ping (keepalive)
ws.send(JSON.stringify({ command: 'ping' }));
```

## React Integration

The file `app/static/realtime-client.js` contains ready-to-use React hooks:

### usePredictionSSE Hook

```jsx
import { usePredictionSSE } from './realtime-client';

function PredictionTracker({ responseId }) {
  const { 
    progress, 
    message, 
    status, 
    result, 
    error, 
    isConnected 
  } = usePredictionSSE(responseId);

  if (status === 'failed') {
    return <div className="error">{error}</div>;
  }

  if (status === 'completed') {
    return <ResultDisplay data={result} />;
  }

  return (
    <div className="tracker">
      <div className="status">
        {isConnected ? '🟢' : '🔴'} {status}
      </div>
      <ProgressBar value={progress} />
      <p>{message}</p>
    </div>
  );
}
```

### usePredictionWebSocket Hook

```jsx
import { usePredictionWebSocket } from './realtime-client';

function PredictionDashboard() {
  const { 
    subscribe, 
    unsubscribe, 
    predictions, 
    isConnected 
  } = usePredictionWebSocket();

  const handleNewPrediction = async (formData) => {
    const response = await fetch('/api/v1/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    const { response_id } = await response.json();
    subscribe(response_id);
  };

  return (
    <div>
      <ConnectionStatus connected={isConnected} />
      
      <PredictionForm onSubmit={handleNewPrediction} />
      
      {Object.entries(predictions).map(([id, state]) => (
        <PredictionCard
          key={id}
          responseId={id}
          progress={state.progress}
          status={state.status}
          result={state.result}
          error={state.error}
          onRemove={() => unsubscribe(id)}
        />
      ))}
    </div>
  );
}
```

## Error Handling

### SSE Reconnection

Browsers automatically reconnect SSE connections. To handle reconnection:

```javascript
eventSource.onerror = (error) => {
  if (eventSource.readyState === EventSource.CONNECTING) {
    console.log('Reconnecting...');
  } else if (eventSource.readyState === EventSource.CLOSED) {
    console.log('Connection closed');
  }
};
```

### WebSocket Reconnection

For WebSockets, implement manual reconnection:

```javascript
function createWebSocket(url, onMessage) {
  let ws;
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 5;
  
  function connect() {
    ws = new WebSocket(url);
    
    ws.onopen = () => {
      console.log('Connected');
      reconnectAttempts = 0;
    };
    
    ws.onmessage = onMessage;
    
    ws.onclose = () => {
      if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        console.log(`Reconnecting in ${delay}ms...`);
        setTimeout(connect, delay);
      }
    };
  }
  
  connect();
  
  return {
    send: (data) => ws.send(JSON.stringify(data)),
    close: () => ws.close()
  };
}
```

## API Reference

### GET /api/v1/realtime/sse/{response_id}

Server-Sent Events stream for a single prediction.

**Response**: SSE stream with events: `connection`, `progress`, `completed`, `failed`, `keepalive`

### WebSocket /api/v1/realtime/ws/{response_id}

WebSocket for a single prediction (auto-subscribes on connect).

**Server Messages**: `status`, `progress`, `completed`, `failed`, `ping`
**Client Commands**: `{"command": "ping"}`, `{"command": "status"}`

### WebSocket /api/v1/realtime/ws

WebSocket for multiple predictions.

**Server Messages**: `connection`, `subscribed`, `unsubscribed`, `status`, `progress`, `completed`, `failed`, `error`, `ping`
**Client Commands**:
- `{"command": "subscribe", "response_id": "..."}`
- `{"command": "unsubscribe", "response_id": "..."}`
- `{"command": "status", "response_id": "..."}`
- `{"command": "list_subscriptions"}`
- `{"command": "ping"}`

### GET /api/v1/realtime/events/{response_id}/history

Get recent event history for a prediction.

**Query Parameters**: `limit` (default: 10, max: 100)

**Response**:
```json
{
  "response_id": "...",
  "events": [...],
  "count": 10
}
```

### GET /api/v1/realtime/stats

Get connection statistics.

**Response**:
```json
{
  "stats": {
    "sse_subscriptions": 5,
    "sse_predictions": 3,
    "ws_connections": 10,
    "ws_subscriptions": 15,
    "event_history_predictions": 50,
    "total_events_in_history": 500
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```
