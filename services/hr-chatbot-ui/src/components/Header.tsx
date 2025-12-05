import { Group, Text, Badge, ActionIcon, useMantineColorScheme } from '@mantine/core';
import { IconSun, IconMoon, IconUser } from '@tabler/icons-react';
import { ConnectionStatus } from '../types/chat';

interface HeaderProps {
  connectionStatus: ConnectionStatus;
}

const getStatusColor = (status: ConnectionStatus): string => {
  switch (status) {
    case 'connected':
      return 'green';
    case 'connecting':
      return 'yellow';
    case 'disconnected':
      return 'gray';
    case 'error':
      return 'red';
    default:
      return 'gray';
  }
};

const getStatusText = (status: ConnectionStatus): string => {
  switch (status) {
    case 'connected':
      return 'Connected';
    case 'connecting':
      return 'Connecting...';
    case 'disconnected':
      return 'Disconnected';
    case 'error':
      return 'Error';
    default:
      return 'Unknown';
  }
};

export const Header = ({ connectionStatus }: HeaderProps) => {
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const userId = import.meta.env.VITE_USER_ID || 'EMP001';

  return (
    // <Group justify="space-between" p="md" style={{ borderBottom: '1px solid var(--mantine-color-gray-3)' }}>
    <Group justify="space-between" p="md">
      <Group>
        <Text fw={600} size="lg">
          HR Chatbot Assistant
        </Text>
        <Badge
          color={getStatusColor(connectionStatus)}
          variant="dot"
          aria-label={`Connection status: ${getStatusText(connectionStatus)}`}
        >
          {getStatusText(connectionStatus)}
        </Badge>
      </Group>

      <Group gap="md">
        <Group gap="xs">
          <IconUser size={16} />
          <Text size="sm" c="dimmed" aria-label={`User ID: ${userId}`}>
            {userId}
          </Text>
        </Group>
        
        <ActionIcon
          variant="default"
          onClick={() => toggleColorScheme()}
          size="lg"
          aria-label={`Switch to ${colorScheme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {colorScheme === 'dark' ? <IconSun size={18} /> : <IconMoon size={18} />}
        </ActionIcon>
      </Group>
    </Group>
  );
};
