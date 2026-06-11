import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileSearch } from 'lucide-react';
import type { Citation } from '../hooks/useChatState';

export function CitationExpander({ citations }: { citations: Citation[] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 border border-slate-200 rounded-md overflow-hidden bg-slate-50 transition-all">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors focus:outline-none"
      >
        <div className="flex items-center">
          <FileSearch className="w-4 h-4 mr-2 text-indigo-500" />
          <span>View Source Citations ({citations.length})</span>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>
      
      {/* Sleek Accordion Expanded State */}
      {isExpanded && (
        <div className="p-4 border-t border-slate-200 bg-white space-y-4">
          {citations.map((cite, idx) => (
            <div key={idx} className="text-sm">
              <div className="flex items-baseline mb-2">
                <span className="font-semibold text-slate-900 mr-2">{cite.filename}</span>
                <span className="text-slate-500 text-xs">Page {cite.page}</span>
              </div>
              <blockquote className="pl-3 border-l-2 border-indigo-200 text-slate-600 bg-slate-50/50 p-3 rounded-r leading-relaxed">
                {cite.snippet}
              </blockquote>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
