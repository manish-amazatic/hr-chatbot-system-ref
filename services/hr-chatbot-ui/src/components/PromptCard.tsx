import { Button } from '@mantine/core';
import { PromptConfig } from '../types/prompts';

interface PromptCardProps {
  prompt: PromptConfig;
  onClick: (promptText: string) => void;
}

export const PromptCard = ({ prompt, onClick }: PromptCardProps) => {
  const handleClick = () => {
    onClick(prompt.prompt);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick();
    }
  };

  return (
    <Button
      variant="light"
      fullWidth
      onClick={handleClick}
      onKeyDown={handleKeyPress}
      aria-label={`Use prompt: ${prompt.label}`}
      tabIndex={0}
      size="sm"
      style={{
        textAlign: 'left',
        height: 'auto',
        padding: '8px 12px',
      }}
    >
      {prompt.label}
    </Button>
  );
};
