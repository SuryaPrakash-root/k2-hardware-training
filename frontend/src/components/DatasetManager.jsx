import { useState, useEffect } from 'react';
import axios from 'axios';

export default function DatasetManager({ refreshTrigger }) {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [datasetDetail, setDatasetDetail] = useState(null);
  const [editing, setEditing] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');
  const [mergeSelection, setMergeSelection] = useState([]);
  const [mergeName, setMergeName] = useState('');

  useEffect(() => {
    loadDatasets();
  }, [refreshTrigger]);

  const loadDatasets = async () => {
    try {
      const res = await axios.get('/api/datasets');
      setDatasets(res.data);
    } catch (e) {
      console.error('Failed to load datasets:', e);
    }
  };

  const loadDatasetDetail = async (name) => {
    try {
      const res = await axios.get(`/api/datasets/${name}`);
      setDatasetDetail(res.data);
      setSelectedDataset(name);
    } catch (e) {
      console.error('Failed to load dataset:', e);
    }
  };

  const handleAddExample = async () => {
    if (!newQuestion || !newAnswer) return;
    try {
      await axios.post(`/api/datasets/${selectedDataset}/add`, {
        question: newQuestion,
        answer: newAnswer,
      });
      setNewQuestion('');
      setNewAnswer('');
      loadDatasetDetail(selectedDataset);
    } catch (e) {
      console.error('Failed to add example:', e);
    }
  };

  const handleDeleteExample = async (index) => {
    try {
      await axios.delete(`/api/datasets/${selectedDataset}/examples/${index}`);
      loadDatasetDetail(selectedDataset);
    } catch (e) {
      console.error('Failed to delete example:', e);
    }
  };

  const handleDeleteDataset = async (name) => {
    if (!confirm(`Delete dataset "${name}"?`)) return;
    try {
      await axios.delete(`/api/datasets/${name}`);
      setSelectedDataset(null);
      setDatasetDetail(null);
      loadDatasets();
    } catch (e) {
      console.error('Failed to delete dataset:', e);
    }
  };

  const handleMerge = async () => {
    if (mergeSelection.length < 2) return;
    try {
      await axios.post('/api/datasets/merge', {
        names: mergeSelection,
        output_name: mergeName || undefined,
      });
      setMergeSelection([]);
      setMergeName('');
      loadDatasets();
    } catch (e) {
      console.error('Failed to merge datasets:', e);
    }
  };

  const toggleMergeSelection = (name) => {
    setMergeSelection(prev =>
      prev.includes(name) ? prev.filter(n => n !== name) : [...prev, name]
    );
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h2 className="text-xl font-semibold text-white mb-4">Dataset Manager</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Datasets ({datasets.length})</h3>
          <div className="space-y-2 max-h-96 overflow-auto">
            {datasets.map((ds) => (
              <div
                key={ds.name}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedDataset === ds.name
                    ? 'bg-blue-600/20 border border-blue-500/50'
                    : 'bg-gray-700/50 hover:bg-gray-700'
                }`}
                onClick={() => loadDatasetDetail(ds.name)}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-200 truncate">{ds.name}</span>
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                    {ds.examples}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{ds.modified}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-700">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Merge Datasets</h3>
            <div className="space-y-2 max-h-32 overflow-auto mb-2">
              {datasets.map((ds) => (
                <label key={ds.name} className="flex items-center gap-2 text-sm text-gray-300">
                  <input
                    type="checkbox"
                    checked={mergeSelection.includes(ds.name)}
                    onChange={() => toggleMergeSelection(ds.name)}
                    className="rounded"
                  />
                  {ds.name}
                </label>
              ))}
            </div>
            <input
              type="text"
              value={mergeName}
              onChange={(e) => setMergeName(e.target.value)}
              placeholder="Output name (optional)"
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-white mb-2"
            />
            <button
              onClick={handleMerge}
              disabled={mergeSelection.length < 2}
              className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm py-2 rounded"
            >
              Merge Selected ({mergeSelection.length})
            </button>
          </div>
        </div>

        <div className="lg:col-span-2">
          {datasetDetail ? (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-white">{datasetDetail.name}</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => setEditing(!editing)}
                    className="text-sm bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded"
                  >
                    {editing ? 'View' : 'Edit'}
                  </button>
                  <button
                    onClick={() => handleDeleteDataset(selectedDataset)}
                    className="text-sm bg-red-600/20 hover:bg-red-600/40 text-red-400 px-3 py-1 rounded"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="bg-gray-900 rounded-lg p-4 max-h-96 overflow-auto">
                {datasetDetail.examples.map((ex, i) => (
                  <div key={i} className="mb-3 p-3 bg-gray-800 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="text-xs text-gray-400 mb-1">Q:</p>
                        <p className="text-sm text-gray-200 mb-2">{ex.text.split('\nAssistant:')[0].replace('User: ', '')}</p>
                        <p className="text-xs text-gray-400 mb-1">A:</p>
                        <p className="text-sm text-gray-300">{ex.text.split('\nAssistant:')[1] || ''}</p>
                      </div>
                      {editing && (
                        <button
                          onClick={() => handleDeleteExample(i)}
                          className="text-red-400 hover:text-red-300 ml-2"
                        >
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {editing && (
                <div className="mt-4 p-4 bg-gray-700/50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Add New Example</h4>
                  <textarea
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                    placeholder="Question"
                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-white mb-2 h-20"
                  />
                  <textarea
                    value={newAnswer}
                    onChange={(e) => setNewAnswer(e.target.value)}
                    placeholder="Answer"
                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm text-white mb-2 h-20"
                  />
                  <button
                    onClick={handleAddExample}
                    disabled={!newQuestion || !newAnswer}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-sm px-4 py-2 rounded"
                  >
                    Add Example
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              <p>Select a dataset to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
