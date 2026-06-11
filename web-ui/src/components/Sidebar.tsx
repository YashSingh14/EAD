import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2 } from 'lucide-react';
import { ControlPanel } from './ControlPanel';
import { ChatState } from '../hooks/useChatState';

export function Sidebar({ chatState }: { chatState: ChatState }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      setFiles(prev => [...prev, ...droppedFiles]);
      await uploadFiles(droppedFiles);
    }
  };

  const uploadFiles = async (filesToUpload: File[]) => {
    setIsUploading(true);
    const formData = new FormData();
    filesToUpload.forEach(f => formData.append('files', f));

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Upload failed');
      const result = await response.json();
      console.log('Upload Result:', result);
      // Optional: Add toast notification for chunks indexed
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-80 flex-shrink-0 bg-slate-50 border-r border-slate-200 h-screen flex flex-col p-6 overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-slate-900 tracking-tight">Enterprise RAG</h1>
        <p className="text-sm text-slate-500 mt-1">Secure semantic intelligence</p>
      </div>

      <ControlPanel chatState={chatState} />

      <div className="mt-8">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
          Document Context
        </h2>
        
        <div 
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center transition-colors cursor-pointer relative
            ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-slate-400 bg-white'}
            ${isUploading ? 'opacity-50 pointer-events-none' : ''}
          `}
        >
          {isUploading ? (
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-3"></div>
          ) : (
            <UploadCloud className={`w-8 h-8 mb-3 transition-colors ${isDragging ? 'text-indigo-500' : 'text-slate-400'}`} />
          )}
          <p className="text-sm text-slate-600 font-medium">
            {isUploading ? 'Vectorizing...' : 'Drag & drop files here'}
          </p>
          <p className="text-xs text-slate-400 mt-1">PDF, DOCX, TXT, HTML</p>
        </div>

        {/* File Roster */}
        {files.length > 0 && (
          <div className="mt-4 space-y-2">
            {files.map((file, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-white border border-slate-200 rounded-md shadow-sm-subtle">
                <div className="flex items-center overflow-hidden">
                  <FileText className="w-4 h-4 text-slate-400 mr-2 flex-shrink-0" />
                  <span className="text-sm text-slate-700 truncate">{file.name}</span>
                </div>
                <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 ml-2" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
