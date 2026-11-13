import { useState, useEffect } from 'react';
import axios from 'axios';

export default function TrainingHistory() {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareSelection, setCompareSelection] = useState([]);
  const [comparison, setComparison] = useState(null);

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const res = await axios.get('/api/train/history');
      setRuns(res.data);
    } catch (e) {
      console.error('Failed to load training history:', e);
    }
  };

  const loadRunDetail = async (runId) => {
    try {
      const res = await axios.get(`/api/train/history/${runId}`);
      setSelectedRun(res.data);
    } catch (e) {
      console.error('Failed to load run:', e);
    }
  };

  const handleDeleteRun = async (runId) => {
    if (!confirm('Delete this training run?')) return;
    try {
      await axios.delete(`/api/train/history/${runId}`);
      setSelectedRun(null);
      loadRuns();
    } catch (e) {
      console.error('Failed to delete run:', e);
    }
  };

  const handleCompare = async () => {
    if (compareSelection.length < 2) return;
    try {
      const res = await axios.post('/api/train/compare', {
        run_ids: compareSelection,
      });
      setComparison(res.data.runs);
    } catch (e) {
      console.error('Failed to compare runs:', e);
    }
  };

  const toggleCompareSelection = (runId) => {
    setCompareSelection(prev =>
      prev.includes(runId) ? prev.filter(id => id !== runId) : [...prev, runId]
    );
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">Training History</h2>
        <button
          onClick={() => {
            setCompareMode(!compareMode);
            setCompareSelection([]);
            setComparison(null);
          }}
          className={`text-sm px-3 py-1 rounded ${
            compareMode ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
          }`}
        >
          {compareMode ? 'Cancel Compare' : 'Compare Runs'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Runs ({runs.length})</h3>
          <div className="space-y-2 max-h-96 overflow-auto">
            {runs.length === 0 ? (
              <p className="text-gray-500 text-sm">No training runs yet</p>
            ) : (
              runs.map((run) => (
                <div
                  key={run.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedRun?.id === run.id
                      ? 'bg-blue-600/20 border border-blue-500/50'
                      : 'bg-gray-700/50 hover:bg-gray-700'
                  }`}
                  onClick={() => compareMode ? toggleCompareSelection(run.id) : loadRunDetail(run.id)}
                >
                  <div className="flex items-center justify-between">
                    {compareMode && (
                      <input
                        type="checkbox"
                        checked={compareSelection.includes(run.id)}
                        onChange={() => toggleCompareSelection(run.id)}
                        className="mr-2"
                      />
                    )}
                    <span className="text-sm text-gray-200">{run.id}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{run.timestamp}</p>
                  {run.metrics && (
                    <div className="flex gap-2 mt-1">
                      <span className="text-xs bg-green-500/20 text-green-400 px-1 rounded">
                        Loss: {run.metrics.train_loss || '-'}
                      </span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {compareMode && compareSelection.length >= 2 && (
            <button
              onClick={handleCompare}
              className="w-full mt-3 bg-blue-600 hover:bg-blue-700 text-white text-sm py-2 rounded"
            >
              Compare Selected ({compareSelection.length})
            </button>
          )}
        </div>

        <div className="lg:col-span-2">
          {comparison ? (
            <div>
              <h3 className="text-lg font-medium text-white mb-4">Comparison</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-2 px-3 text-gray-400">Metric</th>
                      {comparison.map((run) => (
                        <th key={run.id} className="text-left py-2 px-3 text-gray-400">{run.id}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-700/50">
                      <td className="py-2 px-3 text-gray-300">Loss</td>
                      {comparison.map((run) => (
                        <td key={run.id} className="py-2 px-3 text-gray-200">
                          {run.metrics?.train_loss || '-'}
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b border-gray-700/50">
                      <td className="py-2 px-3 text-gray-300">Runtime</td>
                      {comparison.map((run) => (
                        <td key={run.id} className="py-2 px-3 text-gray-200">
                          {run.metrics?.train_runtime || '-'}s
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b border-gray-700/50">
                      <td className="py-2 px-3 text-gray-300">Epochs</td>
                      {comparison.map((run) => (
                        <td key={run.id} className="py-2 px-3 text-gray-200">
                          {run.config?.epochs || '-'}
                        </td>
                      ))}
                    </tr>
                    <tr className="border-b border-gray-700/50">
                      <td className="py-2 px-3 text-gray-300">Learning Rate</td>
                      {comparison.map((run) => (
                        <td key={run.id} className="py-2 px-3 text-gray-200">
                          {run.config?.learning_rate || '-'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="py-2 px-3 text-gray-300">Dataset</td>
                      {comparison.map((run) => (
                        <td key={run.id} className="py-2 px-3 text-gray-200">
                          {run.dataset?.name || '-'}
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          ) : selectedRun ? (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-white">{selectedRun.id}</h3>
                <button
                  onClick={() => handleDeleteRun(selectedRun.id)}
                  className="text-sm bg-red-600/20 hover:bg-red-600/40 text-red-400 px-3 py-1 rounded"
                >
                  Delete
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <p className="text-xs text-gray-400">Status</p>
                  <p className="text-sm text-white capitalize">{selectedRun.status}</p>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <p className="text-xs text-gray-400">Timestamp</p>
                  <p className="text-sm text-white">{selectedRun.timestamp}</p>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <p className="text-xs text-gray-400">Final Loss</p>
                  <p className="text-sm text-white">{selectedRun.metrics?.train_loss || '-'}</p>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <p className="text-xs text-gray-400">Runtime</p>
                  <p className="text-sm text-white">{selectedRun.metrics?.train_runtime || '-'}s</p>
                </div>
              </div>

              <div className="bg-gray-700/50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Configuration</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><span className="text-gray-400">Epochs:</span> <span className="text-gray-200">{selectedRun.config?.epochs}</span></div>
                  <div><span className="text-gray-400">Learning Rate:</span> <span className="text-gray-200">{selectedRun.config?.learning_rate}</span></div>
                  <div><span className="text-gray-400">Batch Size:</span> <span className="text-gray-200">{selectedRun.config?.batch_size}</span></div>
                  <div><span className="text-gray-400">LoRA Rank:</span> <span className="text-gray-200">{selectedRun.config?.lora_rank}</span></div>
                </div>
              </div>

              {selectedRun.dataset && (
                <div className="mt-4 bg-gray-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Dataset</h4>
                  <div className="text-sm">
                    <p><span className="text-gray-400">Name:</span> <span className="text-gray-200">{selectedRun.dataset.name}</span></p>
                    <p><span className="text-gray-400">Examples:</span> <span className="text-gray-200">{selectedRun.dataset.count}</span></p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              <p>Select a training run to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
