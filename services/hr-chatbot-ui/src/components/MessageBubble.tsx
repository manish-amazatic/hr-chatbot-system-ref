import { Paper, Text, Badge, Stack, Group, TypographyStylesProvider, useMantineColorScheme } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatMessage } from '../types/chat';
import { getAgentDisplayName, getAgentColor } from '../utils/agentHelpers';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user';
  const { colorScheme } = useMantineColorScheme();
  const isDark = colorScheme === 'dark';

  return (
    <Stack
      gap="xs"
      align={isUser ? 'flex-end' : 'flex-start'}
      style={{ width: '100%' }}
      role="article"
      aria-label={`${isUser ? 'User' : 'Assistant'} message: ${message.content.substring(0, 50)}`}
    >
      <Group gap="xs" align="center">
        <Text size="xs" fw={600} c={isUser ? 'blue.6' : 'dimmed'}>
          {isUser ? 'Employee' : 'HR Assistant'}
        </Text>
        {!isUser && message.agentUsed && (
          <Badge
            size="sm"
            variant="light"
            color={getAgentColor(message.agentUsed)}
            aria-label={`Handled by ${getAgentDisplayName(message.agentUsed)}`}
          >
            {getAgentDisplayName(message.agentUsed)}
          </Badge>
        )}
      </Group>
      <Paper
        p="md"
        bg={isUser ? 'blue.6' : isDark ? 'dark.6' : 'gray.0'}
        style={{
          maxWidth: '80%',
          color: isUser ? 'white' : isDark ? 'white' : 'inherit',
        }}
      >
        {isUser ? (
          <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>{message.content}</Text>
        ) : (
          <TypographyStylesProvider>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || '_Thinking..._'}
            </ReactMarkdown>
          </TypographyStylesProvider>
        )}
      </Paper>
      
      
      <Text size="xs" c="dimmed">
        {message.timestamp.toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        })}
      </Text>
    </Stack>
  );
};
