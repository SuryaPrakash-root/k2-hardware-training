import { useState } from 'react';
import axios from 'axios';

export default function UrlInput({ onParseComplete }) {
  const [url, setUrl] = useState('');
  const [parsing, setParsing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleParse = async () => {
    if (!url.trim()) return;
    
    setParsing(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await axios.post('/api/parse-url', { url: url.trim() });
      setResult(response.data);
      if (onParseComplete) onParseComplete(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse URL');
    } finally {
      setParsing(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleParse();
  };

  const isYouTube = url.includes('youtube.com') || url.includes('youtu.be');

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h2 className="text-xl font-semibold text-white mb-4">Parse Website or YouTube</h2>
      
      <div className="flex gap-2 mb-4">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="https://example.com or https://youtube.com/watch?v=..."
          className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white text-sm placeholder-gray-400 focus:outline-none focus:border-blue-500"
          disabled={parsing}
        />
        <button
          onClick={handleParse}
          disabled={parsing || !url.trim()}
          className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg text-sm font-medium transition-colors"
        >
          {parsing ? 'Parsing...' : 'Parse'}
        </button>
      </div>

      <div className="flex items-center gap-4 text-xs text-gray-400 mb-4">
        <span className="flex items-center gap-1">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
          Websites
        </span>
        <span className="flex items-center gap-1">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          YouTube
        </span>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4 bg-green-500/10 border border-green-500/50 rounded-lg p-4">
          <h3 className="text-green-400 font-medium mb-2">Parse Successful</h3>
          <div className="text-sm text-gray-300 space-y-1">
            <p>Type: <span className="capitalize">{result.type}</span></p>
            <p>Title: {result.title}</p>
            <p>Text extracted: {result.text_length.toLocaleString()} characters</p>
            <p>Chunks: {result.chunks}</p>
            <p>Q&A pairs generated: {result.examples}</p>
          </div>
          <div className="mt-3">
            <p className="text-xs text-gray-400 mb-1">Preview:</p>
            <pre className="text-xs text-gray-400 bg-gray-900 rounded p-2 max-h-32 overflow-auto">
              {result.preview}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
