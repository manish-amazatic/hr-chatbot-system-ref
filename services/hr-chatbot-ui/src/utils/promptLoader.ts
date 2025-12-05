import promptsData from '../config/prompts.json';
import { PromptCategory } from '../types/prompts';

export const loadPrompts = (): PromptCategory[] => {
  return promptsData as PromptCategory[];
};

export const getAllCategoryIds = (): string[] => {
  return promptsData.map((category) => category.name);
};
