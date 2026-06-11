import React, { useState } from 'react';
import { UploadCloud, FileText } from 'lucide-react';
import { ControlPanel } from './ControlPanel';

export function Sidebar() {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  return (
    <div className="w-80 flex-shrink-0 bg-slate-50 border-r border-slate-200 h-screen flex flex-col p-6 overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-slate-900 tracking-tight">Enterprise RAG</h1>
        <p className="text-sm text-slate-500 mt-1">Secure semantic intelligence</p>
      </div>

      <ControlPanel />

      <div className="mt-8">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
          Document Context
        </h2>
        
        {/* Minimalist Dropzone avoiding neon/glassmorphism */}
        <div 
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center transition-colors cursor-pointer
            ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-slate-400 bg-white'}
          `}
        >
          <UploadCloud className={`w-8 h-8 mb-3 transition-colors ${isDragging ? 'text-indigo-500' : 'text-slate-400'}`} />
          <p className="text-sm text-slate-600 font-medium">Drag & drop files here</p>
          <p className="text-xs text-slate-400 mt-1">PDF, DOCX, TXT, HTML up to 50MB</p>
        </div>

        {/* File Roster */}
        {files.length > 0 && (
          <div className="mt-4 space-y-2">
            {files.map((file, i) => (
              <div key={i} className="flex items-center p-2 bg-white border border-slate-200 rounded-md shadow-sm-subtle">
                <FileText className="w-4 h-4 text-slate-400 mr-2 flex-shrink-0" />
                <span className="text-sm text-slate-700 truncate">{file.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
