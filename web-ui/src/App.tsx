import React from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatContainer } from './components/ChatContainer';
import { useChatState } from './hooks/useChatState';

function App() {
  // Lifted state to pass down configuration and chat methods via props
  const chatState = useChatState();

  return (
    <div className="flex h-screen bg-white font-sans overflow-hidden antialiased text-slate-800">
      <Sidebar chatState={chatState} />
      <ChatContainer chatState={chatState} />
    </div>
  );
}

export default App;
