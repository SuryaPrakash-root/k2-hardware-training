import { useState, useRef, useEffect } from 'react';
import { ragQuery, ragStatus, ragReindex } from '../utils/api';

export default function RagChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [topK, setTopK] = useState(4);
  const messagesEndRef = useRef(null);

  const loadStatus = async () => {
    try {
      const res = await ragStatus();
      setStatus(res.data);
    } catch (e) { /* backend offline */ }
  };

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const res = await ragQuery(question, topK);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.data.answer,
          sources: res.data.sources || [],
        },
      ]);
      loadStatus();
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error: RAG query failed. Is the backend running?', sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleReindex = async () => {
    try {
      await ragReindex();
      loadStatus();
    } catch (e) { /* ignore */ }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => setMessages([]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Index status sidebar */}
      <div className="lg:col-span-1 bg-gray-800 rounded-xl p-5 border border-gray-700 h-fit">
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${status?.vectors > 0 ? 'bg-green-400' : 'bg-gray-500'}`} />
          Vector Index
        </h3>
        {status ? (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Vectors</span>
              <span className="text-white font-medium">{status.vectors}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Documents</span>
              <span className="text-white font-medium">{status.source_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Dimensions</span>
              <span className="text-white font-medium">{status.dimensions}</span>
            </div>
            <div className="text-xs text-gray-500 pt-1 break-all">{status.model}</div>
            {status.sources.length > 0 && (
              <div className="pt-2 border-t border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Indexed sources:</div>
                {status.sources.slice(0, 5).map((s) => (
                  <div key={s} className="text-xs text-gray-300 truncate" title={s}>📄 {s}</div>
                ))}
                {status.sources.length > 5 && (
                  <div className="text-xs text-gray-500">+{status.sources.length - 5} more</div>
                )}
              </div>
            )}
            <button
              onClick={handleReindex}
              className="w-full mt-2 text-xs bg-gray-700 hover:bg-gray-600 text-gray-200 px-3 py-2 rounded-lg transition-colors"
            >
              Rebuild Index
            </button>
          </div>
        ) : (
          <div className="text-sm text-gray-500">Loading status...</div>
        )}

        <div className="mt-4 pt-4 border-t border-gray-700">
          <label className="text-xs text-gray-400 block mb-1">Top-K results: {topK}</label>
          <input
            type="range"
            min="1"
            max="8"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      {/* Chat area */}
      <div className="lg:col-span-3 bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">
            RAG Assistant
            <span className="ml-2 text-xs font-normal bg-purple-600/30 text-purple-300 px-2 py-1 rounded">
              Retrieval-Augmented
            </span>
          </h2>
          {messages.length > 0 && (
            <button onClick={clearChat} className="text-sm text-gray-400 hover:text-white transition-colors">
              Clear
            </button>
          )}
        </div>

        <div className="bg-gray-900 rounded-lg p-4 h-96 overflow-auto mb-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <svg className="h-12 w-12 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <p>Ask questions answered from your uploaded documents</p>
              <p className="text-xs mt-1">Chunks are retrieved by similarity, then grounded by the model</p>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`mb-4 ${msg.role === 'user' ? 'flex justify-end' : ''}`}>
                <div
                  className={`max-w-[85%] rounded-xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-100 border border-gray-700'
                  }`}
                >
                  <div className="text-xs text-gray-400 mb-1">
                    {msg.role === 'user' ? 'You' : 'K2 RAG'}
                  </div>
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <div className="text-xs text-purple-300 mb-1">📚 Retrieved context:</div>
                      {msg.sources.map((s, j) => (
                        <div key={j} className="text-xs text-gray-400 mb-1 flex items-start gap-1">
                          <span className="text-gray-500 shrink-0">
                            [{Math.round(s.score * 100)}%]
                          </span>
                          <span className="truncate" title={s.text}>{s.source}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="mb-4">
              <div className="inline-block bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 max-w-[85%]">
                <div className="text-xs text-gray-400 mb-1">K2 RAG</div>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Retrieving &amp; generating...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask something from your indexed documents..."
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white text-sm placeholder-gray-400 focus:outline-none focus:border-purple-500"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg text-sm font-medium transition-colors"
          >
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}
