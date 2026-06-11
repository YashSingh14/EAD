import { useState } from 'react';

export interface Citation {
  filename: string;
  page: string | number;
  snippet: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export function useChatState() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = (message: Omit<Message, 'id'>) => {
    // Uses standard state management without complex reducers to prevent flickering
    // Generates a local epoch ID for React key rendering
    setMessages(prev => [...prev, { ...message, id: Date.now().toString() }]);
  };

  return {
    messages,
    isLoading,
    setIsLoading,
    addMessage,
  };
}
