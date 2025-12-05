import { createContext, useContext, useState, ReactNode, useCallback, useEffect } from 'react';
import { ChatMessage, ConnectionStatus } from '../types/chat';
import { streamChatMessage, checkHealth } from '../services/chatApi';

interface ChatContextType {
  messages: ChatMessage[];
  connectionStatus: ConnectionStatus;
  isStreaming: boolean;
  sendMessage: (content: string) => void;
  clearMessages: () => void;
  reconnect: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [isStreaming, setIsStreaming] = useState(false);
  const userId = import.meta.env.VITE_USER_ID || 'EMP001';

  const checkConnection = useCallback(async () => {
    const isHealthy = await checkHealth();
    setConnectionStatus(isHealthy ? 'connected' : 'disconnected');
  }, []);

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [checkConnection]);

  const sendMessage = useCallback((content: string) => {
    if (isStreaming || connectionStatus !== 'connected') return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Add assistant message placeholder
    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMessage]);

    setIsStreaming(true);

    // Start streaming
    let accumulatedContent = '';
    
    streamChatMessage(content, userId, {
      onToken: (token) => {
        accumulatedContent += token;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: accumulatedContent }
              : msg
          )
        );
      },
      onDone: (_sessionId, agentUsed) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, isStreaming: false, agentUsed }
              : msg
          )
        );
        setIsStreaming(false);
      },
      onError: (error) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? {
                  ...msg,
                  content: `Error: ${error}`,
                  isStreaming: false,
                }
              : msg
          )
        );
        setIsStreaming(false);
        setConnectionStatus('error');
      },
    });
  }, [isStreaming, connectionStatus, userId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const reconnect = useCallback(() => {
    setConnectionStatus('connecting');
    checkConnection();
  }, [checkConnection]);

  const value: ChatContextType = {
    messages,
    connectionStatus,
    isStreaming,
    sendMessage,
    clearMessages,
    reconnect,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
