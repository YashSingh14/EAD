import React, { useState } from 'react';
import { Send, User, Cpu } from 'lucide-react';
import { useChatState } from '../hooks/useChatState';
import { CitationExpander } from './CitationExpander';

export function ChatContainer() {
  const { messages, isLoading, addMessage, setIsLoading } = useChatState();
  const [input, setInput] = useState('');

  // Example frontend mock handler for demonstration of state management
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    addMessage({ role: 'user', content: input });
    setInput('');
    setIsLoading(true);

    // Simulate backend response payload
    setTimeout(() => {
      addMessage({
        role: 'assistant',
        content: 'Based strictly on the provided documents, the Q3 revenue grew by 14% year-over-year. The primary driver was the new Enterprise SaaS tier launch in EMEA.',
        citations: [
          { filename: 'Q3_Financial_Report.pdf', page: 12, snippet: 'Revenue for the third quarter grew by 14% YoY, largely attributed to the successful rollout of the Enterprise SaaS tier across the EMEA region.' }
        ]
      });
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="h-16 border-b border-slate-200 flex items-center px-8 bg-white/90 backdrop-blur-sm sticky top-0 z-10">
        <h2 className="text-lg font-medium text-slate-800 tracking-tight">Research Assistant</h2>
      </header>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-8 scroll-smooth">
        <div className="max-w-3xl mx-auto space-y-8 pb-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 pt-32">
              <Cpu className="w-12 h-12 mb-4 text-slate-300" />
              <p>Upload documents and ask a question to begin.</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className="flex">
                <div className="mr-4 flex-shrink-0 mt-1">
                  {msg.role === 'user' ? (
                    <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600">
                      <User className="w-4 h-4" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                      <Cpu className="w-4 h-4" />
                    </div>
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className={`max-w-none text-sm leading-relaxed ${
                    msg.role === 'assistant' ? 'text-slate-800' : 'text-slate-700 font-medium'
                  }`}>
                    {msg.content}
                  </div>
                  
                  {msg.citations && msg.citations.length > 0 && (
                    <CitationExpander citations={msg.citations} />
                  )}
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex items-center text-slate-500 text-sm py-2">
              <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3"></div>
              Analyzing semantic context...
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white border-t border-slate-100">
        <div className="max-w-3xl mx-auto relative">
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about the documents..."
              className="w-full pl-4 pr-12 py-3 bg-white border border-slate-300 rounded-lg shadow-sm-subtle focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-shadow text-sm"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 top-2 p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors disabled:opacity-50 disabled:hover:bg-transparent disabled:hover:text-slate-400"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-center mt-3">
            <span className="text-[11px] text-slate-400">AI responses should be verified against provided citations.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
