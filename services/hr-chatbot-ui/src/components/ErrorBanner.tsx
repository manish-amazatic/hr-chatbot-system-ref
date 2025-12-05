import { Alert, Button, Group } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

interface ErrorBannerProps {
  onRetry: () => void;
}

export const ErrorBanner = ({ onRetry }: ErrorBannerProps) => {
  return (
    <Alert
      icon={<IconAlertCircle size={16} />}
      title="Connection Error"
      color="red"
      variant="filled"
      withCloseButton={false}
      m="md"
    >
      <Group justify="space-between" align="center">
        <div>
          Unable to connect to the server. Please check your connection and try again.
        </div>
        <Button
          variant="white"
          size="xs"
          onClick={onRetry}
          aria-label="Retry connection"
        >
          Retry
        </Button>
      </Group>
    </Alert>
  );
};
