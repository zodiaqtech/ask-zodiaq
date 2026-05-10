/**
 * MyZodiaq Real-time Client Examples
 * 
 * This file contains ready-to-use client implementations for:
 * - Server-Sent Events (SSE)
 * - WebSocket connections
 * - React hooks
 * - TypeScript types
 */

// ============================================
// TypeScript Types
// ============================================

interface PredictionEvent {
  type: 'connection' | 'subscribed' | 'unsubscribed' | 'progress' | 'status' | 'completed' | 'failed' | 'keepalive' | 'ping' | 'pong' | 'error';
  response_id: string;
  data: any;
  timestamp: string;
}

interface PredictionProgress {
  progress: number;
  message: string;
}

interface PredictionResult {
  result: any;
}

interface PredictionError {
  error: string;
}

interface SSEClientOptions {
  onProgress?: (data: PredictionProgress) => void;
  onCompleted?: (data: PredictionResult) => void;
  onFailed?: (data: PredictionError) => void;
  onConnected?: (status: string, progress: number) => void;
  onError?: (error: Event) => void;
  baseUrl?: string;
}

interface WebSocketClientOptions {
  onProgress?: (responseId: string, data: PredictionProgress) => void;
  onCompleted?: (responseId: string, data: PredictionResult) => void;
  onFailed?: (responseId: string, data: PredictionError) => void;
  onStatus?: (responseId: string, data: any) => void;
  onSubscribed?: (responseId: string) => void;
  onUnsubscribed?: (responseId: string) => void;
  onError?: (error: Event) => void;
  onClose?: () => void;
  baseUrl?: string;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}


// ============================================
// SSE Client Class
// ============================================

class SSEPredictionClient {
  private eventSource: EventSource | null = null;
  private responseId: string;
  private options: SSEClientOptions;
  private baseUrl: string;

  constructor(responseId: string, options: SSEClientOptions = {}) {
    this.responseId = responseId;
    this.options = options;
    this.baseUrl = options.baseUrl || '/api/v1';
  }

  /**
   * Connect to SSE stream for prediction updates
   */
  connect(): void {
    const url = `${this.baseUrl}/realtime/sse/${this.responseId}`;
    this.eventSource = new EventSource(url);

    // Connection established
    this.eventSource.addEventListener('connection', (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      console.log('SSE Connected:', data);
      this.options.onConnected?.(data.current_status, data.current_progress);
    });

    // Progress updates
    this.eventSource.addEventListener('progress', (event: MessageEvent) => {
      const data: PredictionEvent = JSON.parse(event.data);
      console.log('Progress:', data.data);
      this.options.onProgress?.(data.data);
    });

    // Completed
    this.eventSource.addEventListener('completed', (event: MessageEvent) => {
      const data: PredictionEvent = JSON.parse(event.data);
      console.log('Completed:', data.data);
      this.options.onCompleted?.(data.data);
      this.disconnect(); // Auto-close on completion
    });

    // Failed
    this.eventSource.addEventListener('failed', (event: MessageEvent) => {
      const data: PredictionEvent = JSON.parse(event.data);
      console.log('Failed:', data.data);
      this.options.onFailed?.(data.data);
      this.disconnect(); // Auto-close on failure
    });

    // Keepalive (ignore these, just for connection health)
    this.eventSource.addEventListener('keepalive', () => {
      // Connection is healthy
    });

    // Error handling
    this.eventSource.onerror = (error: Event) => {
      console.error('SSE Error:', error);
      this.options.onError?.(error);
    };
  }

  /**
   * Disconnect from SSE stream
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}


// ============================================
// WebSocket Client Class
// ============================================

class WebSocketPredictionClient {
  private ws: WebSocket | null = null;
  private options: WebSocketClientOptions;
  private baseUrl: string;
  private subscriptions: Set<string> = new Set();
  private reconnectAttempts: number = 0;
  private pingInterval: number | null = null;

  constructor(options: WebSocketClientOptions = {}) {
    this.options = {
      reconnect: true,
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      ...options
    };
    this.baseUrl = options.baseUrl || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1`;
  }

  /**
   * Connect to multi-prediction WebSocket
   */
  connect(): void {
    const url = `${this.baseUrl}/realtime/ws`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.startPingInterval();
      
      // Re-subscribe to any existing subscriptions
      this.subscriptions.forEach(responseId => {
        this.send({ command: 'subscribe', response_id: responseId });
      });
    };

    this.ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
      this.options.onError?.(error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.stopPingInterval();
      this.options.onClose?.();
      
      // Attempt reconnection
      if (this.options.reconnect && this.reconnectAttempts < (this.options.maxReconnectAttempts || 5)) {
        this.reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
        setTimeout(() => this.connect(), this.options.reconnectInterval);
      }
    };
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(data: PredictionEvent): void {
    const { type, response_id } = data;

    switch (type) {
      case 'connection':
        console.log('WebSocket connection confirmed:', data);
        break;

      case 'subscribed':
        console.log('Subscribed to:', response_id);
        this.options.onSubscribed?.(response_id);
        break;

      case 'unsubscribed':
        console.log('Unsubscribed from:', response_id);
        this.options.onUnsubscribed?.(response_id);
        break;

      case 'status':
        this.options.onStatus?.(response_id, data.data);
        break;

      case 'progress':
        this.options.onProgress?.(response_id, data.data);
        break;

      case 'completed':
        this.options.onCompleted?.(response_id, data.data);
        this.subscriptions.delete(response_id);
        break;

      case 'failed':
        this.options.onFailed?.(response_id, data.data);
        this.subscriptions.delete(response_id);
        break;

      case 'ping':
        this.send({ command: 'ping' }); // Respond with pong
        break;

      case 'pong':
        // Server responded to our ping
        break;

      case 'error':
        console.error('Server error:', data);
        break;
    }
  }

  /**
   * Subscribe to a prediction's updates
   */
  subscribe(responseId: string): void {
    this.subscriptions.add(responseId);
    if (this.isConnected()) {
      this.send({ command: 'subscribe', response_id: responseId });
    }
  }

  /**
   * Unsubscribe from a prediction's updates
   */
  unsubscribe(responseId: string): void {
    this.subscriptions.delete(responseId);
    if (this.isConnected()) {
      this.send({ command: 'unsubscribe', response_id: responseId });
    }
  }

  /**
   * Get current status of a prediction
   */
  getStatus(responseId: string): void {
    if (this.isConnected()) {
      this.send({ command: 'status', response_id: responseId });
    }
  }

  /**
   * List current subscriptions
   */
  listSubscriptions(): void {
    if (this.isConnected()) {
      this.send({ command: 'list_subscriptions' });
    }
  }

  /**
   * Send a message
   */
  private send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  /**
   * Start ping interval for keepalive
   */
  private startPingInterval(): void {
    this.pingInterval = window.setInterval(() => {
      this.send({ command: 'ping' });
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop ping interval
   */
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    this.options.reconnect = false; // Prevent reconnection
    this.stopPingInterval();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}


// ============================================
// React Hooks
// ============================================

/**
 * React hook for SSE-based prediction tracking
 * 
 * Usage:
 * ```tsx
 * const { progress, status, result, error, isConnected } = usePredictionSSE(responseId);
 * ```
 */
function usePredictionSSE(responseId: string | null, baseUrl: string = '/api/v1') {
  const [progress, setProgress] = React.useState<number>(0);
  const [message, setMessage] = React.useState<string>('');
  const [status, setStatus] = React.useState<string>('pending');
  const [result, setResult] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [isConnected, setIsConnected] = React.useState<boolean>(false);

  React.useEffect(() => {
    if (!responseId) return;

    const client = new SSEPredictionClient(responseId, {
      baseUrl,
      onConnected: (currentStatus, currentProgress) => {
        setStatus(currentStatus);
        setProgress(currentProgress);
        setIsConnected(true);
      },
      onProgress: (data) => {
        setProgress(data.progress);
        setMessage(data.message);
        setStatus('processing');
      },
      onCompleted: (data) => {
        setProgress(100);
        setStatus('completed');
        setResult(data.result);
        setIsConnected(false);
      },
      onFailed: (data) => {
        setStatus('failed');
        setError(data.error);
        setIsConnected(false);
      },
      onError: () => {
        setIsConnected(false);
      }
    });

    client.connect();

    return () => {
      client.disconnect();
    };
  }, [responseId, baseUrl]);

  return { progress, message, status, result, error, isConnected };
}


/**
 * React hook for WebSocket-based multi-prediction tracking
 * 
 * Usage:
 * ```tsx
 * const { subscribe, unsubscribe, predictions, isConnected } = usePredictionWebSocket();
 * 
 * // Subscribe to a prediction
 * subscribe(responseId);
 * 
 * // Access prediction state
 * const predictionState = predictions[responseId];
 * ```
 */
function usePredictionWebSocket(baseUrl?: string) {
  const [predictions, setPredictions] = React.useState<Record<string, {
    progress: number;
    message: string;
    status: string;
    result: any;
    error: string | null;
  }>>({});
  const [isConnected, setIsConnected] = React.useState<boolean>(false);
  const clientRef = React.useRef<WebSocketPredictionClient | null>(null);

  React.useEffect(() => {
    const client = new WebSocketPredictionClient({
      baseUrl,
      onSubscribed: (responseId) => {
        setPredictions(prev => ({
          ...prev,
          [responseId]: prev[responseId] || {
            progress: 0,
            message: '',
            status: 'pending',
            result: null,
            error: null
          }
        }));
      },
      onUnsubscribed: (responseId) => {
        setPredictions(prev => {
          const { [responseId]: _, ...rest } = prev;
          return rest;
        });
      },
      onStatus: (responseId, data) => {
        setPredictions(prev => ({
          ...prev,
          [responseId]: {
            ...prev[responseId],
            status: data.status,
            progress: data.progress || 0
          }
        }));
      },
      onProgress: (responseId, data) => {
        setPredictions(prev => ({
          ...prev,
          [responseId]: {
            ...prev[responseId],
            progress: data.progress,
            message: data.message,
            status: 'processing'
          }
        }));
      },
      onCompleted: (responseId, data) => {
        setPredictions(prev => ({
          ...prev,
          [responseId]: {
            ...prev[responseId],
            progress: 100,
            status: 'completed',
            result: data.result
          }
        }));
      },
      onFailed: (responseId, data) => {
        setPredictions(prev => ({
          ...prev,
          [responseId]: {
            ...prev[responseId],
            status: 'failed',
            error: data.error
          }
        }));
      },
      onClose: () => setIsConnected(false)
    });

    client.connect();
    clientRef.current = client;

    // Check connection status
    const checkConnection = setInterval(() => {
      setIsConnected(client.isConnected());
    }, 1000);

    return () => {
      clearInterval(checkConnection);
      client.disconnect();
    };
  }, [baseUrl]);

  const subscribe = React.useCallback((responseId: string) => {
    clientRef.current?.subscribe(responseId);
  }, []);

  const unsubscribe = React.useCallback((responseId: string) => {
    clientRef.current?.unsubscribe(responseId);
  }, []);

  return { subscribe, unsubscribe, predictions, isConnected };
}


// ============================================
// Usage Examples
// ============================================

/*
Example 1: Simple SSE Usage (Vanilla JavaScript)
------------------------------------------------

// Start a prediction
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

// Connect to SSE for updates
const eventSource = new EventSource(`/api/v1/realtime/sse/${response_id}`);

eventSource.addEventListener('progress', (event) => {
  const data = JSON.parse(event.data);
  updateProgressBar(data.data.progress);
  updateStatusMessage(data.data.message);
});

eventSource.addEventListener('completed', (event) => {
  const data = JSON.parse(event.data);
  displayResult(data.data.result);
  eventSource.close();
});

eventSource.addEventListener('failed', (event) => {
  const data = JSON.parse(event.data);
  showError(data.data.error);
  eventSource.close();
});


Example 2: WebSocket for Multiple Predictions (Vanilla JavaScript)
-----------------------------------------------------------------

const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws');

ws.onopen = () => {
  console.log('Connected');
  
  // Subscribe to multiple predictions
  ws.send(JSON.stringify({ command: 'subscribe', response_id: 'pred-123' }));
  ws.send(JSON.stringify({ command: 'subscribe', response_id: 'pred-456' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'progress':
      console.log(`Prediction ${data.response_id}: ${data.data.progress}%`);
      break;
    case 'completed':
      console.log(`Prediction ${data.response_id} completed!`, data.data.result);
      break;
    case 'failed':
      console.error(`Prediction ${data.response_id} failed:`, data.data.error);
      break;
  }
};


Example 3: React Component with SSE Hook
----------------------------------------

function PredictionTracker({ responseId }) {
  const { progress, message, status, result, error, isConnected } = usePredictionSSE(responseId);

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (status === 'completed') {
    return <PredictionResult data={result} />;
  }

  return (
    <div className="tracker">
      <div className="connection-status">
        {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>
      <div className="progress-bar">
        <div className="fill" style={{ width: `${progress}%` }} />
      </div>
      <div className="message">{message}</div>
    </div>
  );
}


Example 4: React Component with WebSocket Hook (Multiple Predictions)
---------------------------------------------------------------------

function PredictionDashboard() {
  const { subscribe, unsubscribe, predictions, isConnected } = usePredictionWebSocket();
  const [newPrediction, setNewPrediction] = useState(null);

  const startPrediction = async (formData) => {
    const response = await fetch('/api/v1/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    
    const { response_id } = await response.json();
    subscribe(response_id);
    return response_id;
  };

  return (
    <div className="dashboard">
      <div className="status">
        WebSocket: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>
      
      <PredictionForm onSubmit={startPrediction} />
      
      <div className="predictions-list">
        {Object.entries(predictions).map(([id, state]) => (
          <PredictionCard
            key={id}
            responseId={id}
            {...state}
            onCancel={() => unsubscribe(id)}
          />
        ))}
      </div>
    </div>
  );
}

*/

// Export for ES modules
export {
  SSEPredictionClient,
  WebSocketPredictionClient,
  usePredictionSSE,
  usePredictionWebSocket
};
