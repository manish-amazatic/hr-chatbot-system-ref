import { useState, useEffect, useRef } from 'react';
import { Stack, TextInput, ActionIcon, ScrollArea, Loader, Text, Box } from '@mantine/core';
import { IconSend } from '@tabler/icons-react';
import { useChatContext } from '../contexts/ChatContext';
import { MessageBubble } from './MessageBubble';

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const { messages, connectionStatus, isStreaming, sendMessage } = useChatContext();
  const viewport = useRef<HTMLDivElement>(null);

  const isDisabled = connectionStatus !== 'connected' || isStreaming;

  useEffect(() => {
    // Auto-scroll to bottom when messages change
    if (viewport.current) {
      viewport.current.scrollTo({
        top: viewport.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isDisabled) return;

    sendMessage(input.trim());
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Stack
      style={{ height: '100%', position: 'relative' }}
      gap={0}
    >
      <ScrollArea
        style={{ flex: 1 }}
        viewportRef={viewport}
        type="auto"
      >
        <Stack gap="lg" p="md" style={{ minHeight: '100%' }}>
          {messages.length === 0 ? (
            <Box style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '100%',
              minHeight: '400px'
            }}>
              <Text c="dimmed" ta="center">
                Welcome! Select a prompt from the sidebar or type your question below.
              </Text>
            </Box>
          ) : (
            <>
              <div
                role="log"
                aria-live="polite"
                aria-atomic="false"
                aria-label="Chat messages"
              >
                {messages.map((message) => (
                  <Box key={message.id} mb="lg">
                    <MessageBubble message={message} />
                  </Box>
                ))}
              </div>
              {isStreaming && (
                <Box style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Loader size="xs" />
                  <Text size="sm" c="dimmed">
                    Assistant is typing...
                  </Text>
                </Box>
              )}
            </>
          )}
        </Stack>
      </ScrollArea>

      <Box p="md" style={{ borderTop: '1px solid var(--mantine-color-gray-3)' }}>
        <form onSubmit={handleSubmit}>
          <TextInput
            placeholder={
              isDisabled
                ? connectionStatus === 'connected'
                  ? 'Please wait...'
                  : 'Connecting to server...'
                : 'Type your message here...'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={isDisabled}
            rightSection={
              <ActionIcon
                type="submit"
                variant="filled"
                disabled={isDisabled || !input.trim()}
                aria-label="Send message"
              >
                <IconSend size={18} />
              </ActionIcon>
            }
            size="md"
            aria-label="Message input"
          />
        </form>
      </Box>
    </Stack>
  );
};
