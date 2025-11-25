import React, { createContext, useContext, useState, useEffect } from 'react';
import { Session, Message, ChatContextType } from '../types/chat.types';
import { chatService } from '../services/chatService';
import { useAuth } from './AuthContext';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadSessions();
    }
  }, [isAuthenticated]);

  const loadSessions = async () => {
    try {
      const fetchedSessions = await chatService.getSessions();
      setSessions(fetchedSessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createSession = async () => {
    try {
      const newSession = await chatService.createSession('New Chat');
      setSessions([newSession, ...sessions]);
      setCurrentSession(newSession);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create session:', error);
      throw error;
    }
  };

  const selectSession = async (sessionId: string) => {
    try {
      setIsLoading(true);
      const session = await chatService.getSession(sessionId);
      const sessionMessages = await chatService.getMessages(sessionId);
      setCurrentSession(session);
      setMessages(sessionMessages);
    } catch (error) {
      console.error('Failed to select session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await chatService.deleteSession(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      throw error;
    }
  };

  const sendMessage = async (message: string) => {
    if (!currentSession) {
      // Create a new session if none exists
      await createSession();
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        message,
        sessionId: currentSession?.id,
      });

      const assistantMessage: Message = {
        id: response.id,
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp,
        sources: response.sources,
        agentUsed: response.agentUsed,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Update session title if it's the first message
      if (messages.length === 0 && currentSession) {
        const updatedSession = { ...currentSession, title: message.slice(0, 50) };
        setCurrentSession(updatedSession);
        setSessions((prev) =>
          prev.map((s) => (s.id === currentSession.id ? updatedSession : s))
        );
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value: ChatContextType = {
    sessions,
    currentSession,
    messages,
    isLoading,
    createSession,
    selectSession,
    deleteSession,
    sendMessage,
    loadSessions,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
