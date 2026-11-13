import { useState, useEffect, useRef } from 'react';
import { getTrainingStatus, createTrainWebSocket } from '../utils/api';

export default function TrainingMonitor({ trainingStatus, onStatusUpdate }) {
  const [state, setState] = useState({
    status: 'idle',
    progress: 0,
    epoch: 0,
    total_epochs: 3,
    loss: 0,
    step: 0,
    total_steps: 99,
    log: [],
    start_time: null,
    end_time: null,
    error: null,
  });
  const wsRef = useRef(null);
  const logEndRef = useRef(null);

  useEffect(() => {
    if (trainingStatus === 'training') {
      connectWebSocket();
    } else {
      fetchStatus();
    }
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [trainingStatus]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.log]);

  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close();

    const ws = createTrainWebSocket();
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setState(data);
      if (onStatusUpdate) onStatusUpdate(data.status);
    };

    ws.onerror = () => {
      const interval = setInterval(async () => {
        try {
          const res = await getTrainingStatus();
          setState(res.data);
          if (res.data.status !== 'training') clearInterval(interval);
        } catch (e) {}
      }, 2000);
    };

    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send('ping');
    }, 2000);

    ws.onclose = () => clearInterval(pingInterval);
  };

  const fetchStatus = async () => {
    try {
      const res = await getTrainingStatus();
      setState(res.data);
    } catch (e) {}
  };

  const statusColors = {
    idle: 'text-gray-400',
    training: 'text-blue-400',
    completed: 'text-green-400',
    error: 'text-red-400',
    stopped: 'text-yellow-400',
  };

  const statusLabels = {
    idle: 'Idle',
    training: 'Training',
    completed: 'Completed',
    error: 'Error',
    stopped: 'Stopped',
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">Training Monitor</h2>
        <span className={`text-sm font-medium ${statusColors[state.status]}`}>
          {statusLabels[state.status]}
        </span>
      </div>

      {state.status === 'training' && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-400 mb-1">
            <span>Step {state.step} / {state.total_steps}</span>
            <span>{state.progress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${state.progress}%` }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="bg-gray-700/50 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-400">Epoch</p>
          <p className="text-lg font-semibold text-white">{state.epoch}/{state.total_epochs}</p>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-400">Loss</p>
          <p className="text-lg font-semibold text-white">{state.loss.toFixed(4)}</p>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-400">Speed</p>
          <p className="text-lg font-semibold text-white">
            {state.start_time && state.step > 0
              ? `${(state.step / ((Date.now() - new Date(state.start_time).getTime()) / 1000)).toFixed(1)} steps/s`
              : '-'}
          </p>
        </div>
      </div>

      {state.error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm mb-4">
          {state.error}
        </div>
      )}

      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-2">Training Log</h3>
        <div className="bg-gray-900 rounded-lg p-3 h-48 overflow-auto font-mono text-xs">
          {state.log.length === 0 ? (
            <p className="text-gray-500">No log output yet</p>
          ) : (
            state.log.map((line, i) => (
              <div key={i} className="text-gray-300 whitespace-pre-wrap">{line}</div>
            ))
          )}
          <div ref={logEndRef} />
        </div>
      </div>
    </div>
  );
}
