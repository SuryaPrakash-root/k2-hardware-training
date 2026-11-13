import { useState, useRef } from 'react';
import { uploadFile } from '../utils/api';
import UrlInput from './UrlInput';

export default function UploadPanel({ onUploadComplete }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('documents');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) handleUpload(file);
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const response = await uploadFile(file);
      setResult(response.data);
      if (onUploadComplete) onUploadComplete(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const documentExtensions = '.pdf,.docx,.txt,.md';
  const imageExtensions = '.png,.jpg,.jpeg,.bmp,.tiff,.tif,.webp';
  const audioExtensions = '.mp3,.wav,.m4a,.ogg,.flac,.wma,.aac';
  const allExtensions = `${documentExtensions},${imageExtensions},${audioExtensions}`;

  const getAccept = () => {
    if (activeTab === 'documents') return documentExtensions;
    if (activeTab === 'images') return imageExtensions;
    if (activeTab === 'audio') return audioExtensions;
    return allExtensions;
  };

  const getHint = () => {
    if (activeTab === 'documents') return 'PDF, DOCX, TXT, MD';
    if (activeTab === 'images') return 'PNG, JPG, BMP, TIFF, WebP';
    if (activeTab === 'audio') return 'MP3, WAV, M4A, OGG, FLAC';
    return 'All supported formats';
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4">Upload Files</h2>

        <div className="flex gap-2 mb-4">
          {['documents', 'images', 'audio', 'all'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragging
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-gray-600 hover:border-gray-500'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={getAccept()}
            onChange={handleFileSelect}
            className="hidden"
          />

          {uploading ? (
            <div className="text-blue-400">
              <svg className="animate-spin h-8 w-8 mx-auto mb-2" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <p>Processing {activeTab === 'images' ? 'OCR' : activeTab === 'audio' ? 'transcription' : 'file'}...</p>
            </div>
          ) : (
            <>
              {activeTab === 'images' ? (
                <svg className="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              ) : activeTab === 'audio' ? (
                <svg className="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              ) : (
                <svg className="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              )}
              <p className="text-gray-300 mb-1">Drag & drop or click to upload</p>
              <p className="text-gray-500 text-sm">{getHint()}</p>
            </>
          )}
        </div>

        {error && (
          <div className="mt-4 bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 bg-green-500/10 border border-green-500/50 rounded-lg p-4">
            <h3 className="text-green-400 font-medium mb-2">Upload Successful</h3>
            <div className="text-sm text-gray-300 space-y-1">
              <p>File: {result.filename}</p>
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

      <UrlInput onParseComplete={onUploadComplete} />
    </div>
  );
}
