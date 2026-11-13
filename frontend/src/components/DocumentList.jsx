import { useState, useEffect } from 'react';
import { getDocuments, getDatasets, mergeDatasets } from '../utils/api';

export default function DocumentList({ refreshTrigger }) {
  const [documents, setDocuments] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [merging, setMerging] = useState(false);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    try {
      const [docsRes, datasetsRes] = await Promise.all([
        getDocuments(),
        getDatasets(),
      ]);
      setDocuments(docsRes.data);
      setDatasets(datasetsRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const handleMerge = async () => {
    setMerging(true);
    try {
      await mergeDatasets();
      await loadData();
    } catch (err) {
      console.error('Merge failed:', err);
    } finally {
      setMerging(false);
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">Documents & Datasets</h2>
        <button
          onClick={handleMerge}
          disabled={merging || datasets.length < 2}
          className="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm rounded-lg transition-colors"
        >
          {merging ? 'Merging...' : 'Merge All'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">Uploaded Files</h3>
          {documents.length === 0 ? (
            <p className="text-gray-500 text-sm">No files uploaded yet</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-auto">
              {documents.map((doc) => (
                <div key={doc.name} className="bg-gray-700/50 rounded-lg p-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-sm text-gray-300 truncate">{doc.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{formatSize(doc.size)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">Generated Datasets</h3>
          {datasets.length === 0 ? (
            <p className="text-gray-500 text-sm">No datasets generated yet</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-auto">
              {datasets.map((ds) => (
                <div key={ds.name} className="bg-gray-700/50 rounded-lg p-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300 truncate">{ds.name}</span>
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                      {ds.examples} examples
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
