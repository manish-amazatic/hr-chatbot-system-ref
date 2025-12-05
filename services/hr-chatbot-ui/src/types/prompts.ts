export interface PromptConfig {
  id: string;
  category: string;
  icon: string;
  label: string;
  prompt: string;
}

export interface PromptCategory {
  name: string;
  icon: string;
  prompts: PromptConfig[];
}
