import React, { useState } from 'react';
import { Settings2 } from 'lucide-react';

export function ControlPanel() {
  const [provider, setProvider] = useState<'local' | 'cloud'>('local');

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm-subtle">
      <div className="flex items-center text-slate-700 font-medium mb-3">
        <Settings2 className="w-4 h-4 mr-2" />
        <span className="text-sm">LLM Engine</span>
      </div>
      
      {/* Sleek Segmented Control for Engine Toggle */}
      <div className="flex bg-slate-100 p-1 rounded-md mb-4">
        <button
          onClick={() => setProvider('local')}
          className={`flex-1 text-xs font-medium py-1.5 rounded transition-colors ${
            provider === 'local' ? 'bg-white text-slate-900 shadow-sm-subtle' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Local SLM
        </button>
        <button
          onClick={() => setProvider('cloud')}
          className={`flex-1 text-xs font-medium py-1.5 rounded transition-colors ${
            provider === 'cloud' ? 'bg-white text-slate-900 shadow-sm-subtle' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Cloud API
        </button>
      </div>
      
      <div className="space-y-1">
        <label className="text-xs text-slate-500 font-medium">Model Profile</label>
        <input 
          type="text" 
          defaultValue={provider === 'local' ? 'mistral' : 'gemini-1.5-flash'}
          className="w-full text-sm p-2 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
    </div>
  );
}
