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
  const [provider, setProvider] = useState<'local' | 'cloud'>('local');
  const [modelName, setModelName] = useState('mistral');

  const addMessage = (message: Omit<Message, 'id'>) => {
    setMessages(prev => [...prev, { ...message, id: Date.now().toString() }]);
  };

  return {
    messages,
    isLoading,
    setIsLoading,
    addMessage,
    provider,
    setProvider,
    modelName,
    setModelName
  };
}

export type ChatState = ReturnType<typeof useChatState>;
