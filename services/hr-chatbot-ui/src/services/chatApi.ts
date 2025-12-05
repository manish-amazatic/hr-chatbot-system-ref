import { StreamEvent } from '../types/chat';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface StreamCallbacks {
  onToken: (content: string) => void;
  onDone: (sessionId: string, agentUsed?: string) => void;
  onError: (error: string) => void;
}

export const streamChatMessage = (
  message: string,
  userId: string,
  callbacks: StreamCallbacks
): (() => void) => {
  const { onToken, onDone, onError } = callbacks;
  
  let abortController = new AbortController();

  // Use fetch with ReadableStream for SSE since EventSource doesn't support POST
  const startStreaming = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/message/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          user_id: userId,
        }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is not readable');
      }

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamEvent = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'token':
                  if (data.content) {
                    onToken(data.content);
                  }
                  break;
                case 'done':
                  onDone(data.session_id || 'unknown', data.agent_used);
                  return;
                case 'error':
                  onError(data.error || 'Unknown error occurred');
                  return;
              }
            } catch (parseError) {
              console.error('Error parsing SSE line:', parseError, line);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Stream aborted');
        return;
      }
      console.error('Streaming error:', error);
      onError('Connection to server lost. Please try again.');
    }
  };

  startStreaming();

  // Return cleanup function
  return () => {
    abortController.abort();
  };
};

export const sendChatMessage = async (message: string, userId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
};
