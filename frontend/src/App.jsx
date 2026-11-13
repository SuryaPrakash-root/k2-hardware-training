import { useState, useEffect } from 'react';
import UploadPanel from './components/UploadPanel';
import DocumentList from './components/DocumentList';
import DatasetManager from './components/DatasetManager';
import TrainingConfig from './components/TrainingConfig';
import TrainingMonitor from './components/TrainingMonitor';
import TrainingHistory from './components/TrainingHistory';
import ChatInterface from './components/ChatInterface';
import RagChat from './components/RagChat';
import LogsPanel from './components/LogsPanel';
import { getTrainingStatus } from './utils/api';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [trainingStatus, setTrainingStatus] = useState('idle');
  const [activeTab, setActiveTab] = useState('upload');

  useEffect(() => {
    checkTrainingStatus();
    const interval = setInterval(checkTrainingStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkTrainingStatus = async () => {
    try {
      const res = await getTrainingStatus();
      setTrainingStatus(res.data.status);
    } catch (e) {}
  };

  const handleUploadComplete = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleTrainingStart = () => {
    setTrainingStatus('training');
    setActiveTab('monitor');
  };

  const tabs = [
    { id: 'upload', label: 'Upload' },
    { id: 'datasets', label: 'Datasets' },
    { id: 'train', label: 'Train' },
    { id: 'monitor', label: 'Monitor' },
    { id: 'history', label: 'History' },
    { id: 'test', label: 'Test' },
    { id: 'rag', label: 'RAG' },
    { id: 'logs', label: 'Logs' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">K2 Training Platform</h1>
            <p className="text-sm text-gray-400">Fine-tune K2 Horizon on your documents</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${
              trainingStatus === 'training' ? 'bg-blue-400 animate-pulse' :
              trainingStatus === 'completed' ? 'bg-green-400' :
              'bg-gray-500'
            }`} />
            <span className="text-sm text-gray-400 capitalize">{trainingStatus}</span>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800/50 border-b border-gray-700 px-6">
        <div className="max-w-7xl mx-auto flex gap-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* All tabs stay mounted — only visibility toggles, so state
            (chat history, uploads, forms) survives tab switches */}
        <div className={activeTab === 'upload' ? '' : 'hidden'}>
          <UploadPanel onUploadComplete={handleUploadComplete} />
        </div>

        <div className={activeTab === 'datasets' ? '' : 'hidden'}>
          <DatasetManager refreshTrigger={refreshTrigger} />
        </div>

        <div className={activeTab === 'train' ? '' : 'hidden'}>
          <div className="space-y-6">
            <TrainingConfig
              onTrainingStart={handleTrainingStart}
              trainingStatus={trainingStatus}
            />
            <DocumentList refreshTrigger={refreshTrigger} />
          </div>
        </div>

        <div className={activeTab === 'monitor' ? '' : 'hidden'}>
          <TrainingMonitor
            trainingStatus={trainingStatus}
            onStatusUpdate={setTrainingStatus}
          />
        </div>

        <div className={activeTab === 'history' ? '' : 'hidden'}>
          <TrainingHistory />
        </div>

        <div className={activeTab === 'test' ? '' : 'hidden'}>
          <ChatInterface />
        </div>

        <div className={activeTab === 'rag' ? '' : 'hidden'}>
          <RagChat />
        </div>

        <div className={activeTab === 'logs' ? '' : 'hidden'}>
          <LogsPanel />
        </div>
      </main>
    </div>
  );
}

export default App;
