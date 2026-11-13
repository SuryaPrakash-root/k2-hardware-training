import { useState, useEffect, useRef } from 'react';
import { getTrainingStatus } from '../utils/api';

export default function LogsPanel() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef(null);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (autoScroll) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const fetchLogs = async () => {
    try {
      const res = await getTrainingStatus();
      if (res.data.log && res.data.log.length > 0) {
        const newLogs = res.data.log.map((line, i) => ({
          id: i,
          text: line,
          type: detectLogType(line),
          timestamp: new Date().toISOString(),
        }));
        setLogs(newLogs);
      }
    } catch (e) {}
  };

  const detectLogType = (line) => {
    if (line.toLowerCase().includes('error') || line.toLowerCase().includes('failed')) return 'error';
    if (line.toLowerCase().includes('warning')) return 'warning';
    if (line.toLowerCase().includes('loss') || line.toLowerCase().includes('step')) return 'training';
    if (line.toLowerCase().includes('loading') || line.toLowerCase().includes('model')) return 'info';
    return 'default';
  };

  const typeColors = {
    error: 'text-red-400 bg-red-500/10',
    warning: 'text-yellow-400 bg-yellow-500/10',
    training: 'text-blue-400',
    info: 'text-green-400',
    default: 'text-gray-300',
  };

  const filteredLogs = filter === 'all'
    ? logs
    : logs.filter((log) => log.type === filter);

  const clearLogs = () => setLogs([]);

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">Logs</h2>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded"
            />
            Auto-scroll
          </label>
          <button
            onClick={clearLogs}
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        {['all', 'training', 'info', 'warning', 'error'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-3 py-1 text-xs rounded-lg transition-colors ${
              filter === type
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      <div className="bg-gray-900 rounded-lg p-4 h-96 overflow-auto font-mono text-xs">
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <svg className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>No logs yet</p>
            <p className="text-xs mt-1">Logs will appear when training or processing files</p>
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className={`py-1 px-2 rounded mb-0.5 ${typeColors[log.type]}`}
            >
              <span className="text-gray-500 mr-2">[{log.type.toUpperCase()}]</span>
              {log.text}
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
        <span>{filteredLogs.length} log entries</span>
        <span>Auto-refreshing every 2s</span>
      </div>
    </div>
  );
}
