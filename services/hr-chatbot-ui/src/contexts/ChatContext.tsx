import React, { createContext, useContext, useState, useEffect } from 'react';
import { Session, Message, ChatContextType } from '../types/chat.types';
import { chatService } from '../services/chatService';
import { useAuth } from './AuthContext';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
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
      const newSession = await chatService.createSession({
        user_id: user?.id,
        title: 'New Chat'
      });
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

      // Map backend message format to UI format
      const mappedMessages: Message[] = sessionMessages.map((msg: any, index: number) => ({
        id: msg.id || `msg-${index}-${Date.now()}`,
        role: msg.type === 'human' ? 'user' : msg.type === 'ai' ? 'assistant' : (msg.role || 'assistant'),
        content: msg.content,
        timestamp: msg.timestamp || new Date().toISOString(),
        sources: msg.sources,
        agentUsed: msg.agent_used || msg.agentUsed,
      }));

      setCurrentSession(session);
      setMessages(mappedMessages);
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

  const sendMessage = async (message: string, useStreaming: boolean = true) => {
    if (!currentSession) {
      // Create a new session if none exists
      await createSession();
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (useStreaming) {
        // Streaming mode
        const assistantMessageId = `assistant-${Date.now()}`;
        let streamedContent = '';
        let receivedSessionId: string | null = null;
        let agentUsed: string | null = null;

        // Add placeholder message for streaming
        const placeholderMessage: Message = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, placeholderMessage]);

        await chatService.sendMessageStream(
          {
            message,
            sessionId: currentSession?.id,
          },
          // onChunk
          (chunk: string) => {
            streamedContent += chunk;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: streamedContent }
                  : msg
              )
            );
          },
          // onSessionId
          (sessionId: string) => {
            receivedSessionId = sessionId;
          },
          // onComplete
          (agent: string) => {
            agentUsed = agent;
          }
        );

        // Update final message with agent info
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, agentUsed: agentUsed || undefined, timestamp: new Date().toISOString() }
              : msg
          )
        );

        // Update session if needed
        if (receivedSessionId && (!currentSession || currentSession.id !== receivedSessionId)) {
          const newSession = await chatService.getSession(receivedSessionId);
          setCurrentSession(newSession);
        }
      } else {
        // Non-streaming mode
        const response = await chatService.sendMessage({
          message,
          sessionId: currentSession?.id,
        });

        // Update session ID if it was created by the backend
        if (response.session_id && (!currentSession || currentSession.id !== response.session_id)) {
          const newSession = await chatService.getSession(response.session_id);
          setCurrentSession(newSession);
        }

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.response,
          timestamp: response.timestamp,
          sources: response.sources,
          agentUsed: response.agent_used,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      }

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
    setCurrentSession,
    setMessages,
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
