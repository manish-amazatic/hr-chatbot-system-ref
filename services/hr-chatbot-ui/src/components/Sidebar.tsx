import { Stack, Title, Accordion } from '@mantine/core';
import {
  IconCalendar,
  IconClock,
  IconCurrencyDollar,
  IconBook,
} from '@tabler/icons-react';
import { loadPrompts, getAllCategoryIds } from '../utils/promptLoader';
import { PromptCard } from './PromptCard';

interface SidebarProps {
  onPromptSelect: (prompt: string) => void;
}

const iconMap: Record<string, React.ReactNode> = {
  IconCalendar: <IconCalendar size={18} />,
  IconClock: <IconClock size={18} />,
  IconCurrencyDollar: <IconCurrencyDollar size={18} />,
  IconBook: <IconBook size={18} />,
};

export const Sidebar = ({ onPromptSelect }: SidebarProps) => {
  const categories = loadPrompts();
  const defaultOpenCategories = getAllCategoryIds();

  return (
    <Stack gap="md" p="md" style={{ height: '100%', overflowY: 'auto' }}>
      <Title order={3} size="h4">
        Quick Prompts
      </Title>

      <Accordion
        multiple
        defaultValue={defaultOpenCategories}
        variant="separated"
        styles={{
          item: {
            marginBottom: 8,
          },
        }}
      >
        {categories.map((category) => (
          <Accordion.Item key={category.name} value={category.name}>
            <Accordion.Control icon={iconMap[category.icon]}>
              {category.name}
            </Accordion.Control>
            <Accordion.Panel>
              <Stack gap="xs">
                {category.prompts.map((prompt) => (
                  <PromptCard
                    key={prompt.id}
                    prompt={prompt}
                    onClick={onPromptSelect}
                  />
                ))}
              </Stack>
            </Accordion.Panel>
          </Accordion.Item>
        ))}
      </Accordion>
    </Stack>
  );
};
