import { useState } from 'react';
import { startTraining } from '../utils/api';
import axios from 'axios';

export default function TrainingConfig({ onTrainingStart, trainingStatus }) {
  const [mode, setMode] = useState('basic');
  const [config, setConfig] = useState({
    epochs: 3,
    learning_rate: 2e-5,
    batch_size: 2,
    lora_rank: 8,
    max_length: 256,
    qlora: false,
    cosine: true,
    multiturn: false,
    filter_data: true,
  });
  const [starting, setStarting] = useState(false);
  const [searchRunning, setSearchRunning] = useState(false);

  const handleStart = async () => {
    setStarting(true);
    try {
      if (mode === 'basic') {
        await startTraining({
          epochs: config.epochs,
          learning_rate: config.learning_rate,
          batch_size: config.batch_size,
          lora_rank: config.lora_rank,
          max_length: config.max_length,
        });
      } else {
        await axios.post('/api/train/advanced', config);
      }
      if (onTrainingStart) onTrainingStart();
    } catch (err) {
      console.error('Training failed to start:', err);
    } finally {
      setStarting(false);
    }
  };

  const handleHyperSearch = async () => {
    setSearchRunning(true);
    try {
      await axios.post('/api/hyperparameter/search', { max_trials: 6 });
      alert('Hyperparameter search started! Check History tab for results.');
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setSearchRunning(false);
    }
  };

  const isTraining = trainingStatus === 'training';

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h2 className="text-xl font-semibold text-white mb-4">Training Configuration</h2>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setMode('basic')}
          className={`px-4 py-2 text-sm rounded-lg transition-colors ${
            mode === 'basic' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'
          }`}
        >
          Basic
        </button>
        <button
          onClick={() => setMode('advanced')}
          className={`px-4 py-2 text-sm rounded-lg transition-colors ${
            mode === 'advanced' ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-400'
          }`}
        >
          Advanced (QLoRA)
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Epochs</label>
          <input
            type="number"
            value={config.epochs}
            onChange={(e) => setConfig({ ...config, epochs: parseInt(e.target.value) || 3 })}
            disabled={isTraining}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm disabled:opacity-50"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">Learning Rate</label>
          <input
            type="number"
            step="0.000001"
            value={config.learning_rate}
            onChange={(e) => setConfig({ ...config, learning_rate: parseFloat(e.target.value) || 2e-5 })}
            disabled={isTraining}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm disabled:opacity-50"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">Batch Size</label>
          <input
            type="number"
            value={config.batch_size}
            onChange={(e) => setConfig({ ...config, batch_size: parseInt(e.target.value) || 2 })}
            disabled={isTraining}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm disabled:opacity-50"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">LoRA Rank</label>
          <input
            type="number"
            value={config.lora_rank}
            onChange={(e) => setConfig({ ...config, lora_rank: parseInt(e.target.value) || 8 })}
            disabled={isTraining}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm disabled:opacity-50"
          />
        </div>

        <div className="col-span-2">
          <label className="block text-sm text-gray-400 mb-1">Max Sequence Length</label>
          <input
            type="number"
            value={config.max_length}
            onChange={(e) => setConfig({ ...config, max_length: parseInt(e.target.value) || 256 })}
            disabled={isTraining}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm disabled:opacity-50"
          />
        </div>
      </div>

      {mode === 'advanced' && (
        <div className="mb-6 p-4 bg-gray-700/50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-300 mb-3">Advanced Options</h3>
          <div className="grid grid-cols-2 gap-3">
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={config.qlora}
                onChange={(e) => setConfig({ ...config, qlora: e.target.checked })}
                disabled={isTraining}
                className="rounded"
              />
              QLoRA (4-bit quantization)
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={config.cosine}
                onChange={(e) => setConfig({ ...config, cosine: e.target.checked })}
                disabled={isTraining}
                className="rounded"
              />
              Cosine LR Scheduler
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={config.multiturn}
                onChange={(e) => setConfig({ ...config, multiturn: e.target.checked })}
                disabled={isTraining}
                className="rounded"
              />
              Multi-turn Training
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={config.filter_data}
                onChange={(e) => setConfig({ ...config, filter_data: e.target.checked })}
                disabled={isTraining}
                className="rounded"
              />
              Data Quality Filter
            </label>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={handleStart}
          disabled={isTraining || starting}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {starting ? 'Starting...' : isTraining ? 'Training...' : mode === 'advanced' ? 'Start Advanced Training' : 'Start Training'}
        </button>

        <button
          onClick={handleHyperSearch}
          disabled={isTraining || searchRunning}
          className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {searchRunning ? 'Searching...' : 'Auto-Tune'}
        </button>

        {isTraining && (
          <button
            onClick={async () => {
              await axios.post('/api/train/stop');
            }}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Stop
          </button>
        )}
      </div>

      <div className="mt-4 text-xs text-gray-500">
        <p><strong>QLoRA:</strong> 4-bit quantization for faster training with less memory</p>
        <p><strong>Cosine Scheduler:</strong> Better learning rate decay for faster convergence</p>
        <p><strong>Multi-turn:</strong> Train on conversation format for better dialogue</p>
        <p><strong>Data Filter:</strong> Auto-remove low-quality examples</p>
        <p><strong>Auto-Tune:</strong> Search optimal hyperparameters automatically</p>
      </div>
    </div>
  );
}
