import { createTheme, MantineColorsTuple } from '@mantine/core';

const brandBlue: MantineColorsTuple = [
  '#e6f2ff',
  '#cce0ff',
  '#99c2ff',
  '#66a3ff',
  '#3385ff',
  '#0066ff',
  '#0052cc',
  '#003d99',
  '#002966',
  '#001433',
];

export const theme = createTheme({
  primaryColor: 'brandBlue',
  colors: {
    brandBlue,
  },
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  headings: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontWeight: '600',
  },
  defaultRadius: 'md',
  components: {
    Button: {
      defaultProps: {
        radius: 'md',
      },
    },
    TextInput: {
      defaultProps: {
        radius: 'md',
      },
    },
    Paper: {
      defaultProps: {
        radius: 'md',
        shadow: 'sm',
      },
    },
  },
});
