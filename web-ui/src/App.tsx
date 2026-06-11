import React from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatContainer } from './components/ChatContainer';

function App() {
  return (
    <div className="flex h-screen bg-white font-sans overflow-hidden antialiased text-slate-800">
      {/* 
        Main Layout Structure: 
        A fixed-width sidebar for document management (Sidebar)
        and an expansive, center-weighted main chat area (ChatContainer).
      */}
      <Sidebar />
      <ChatContainer />
    </div>
  );
}

export default App;
