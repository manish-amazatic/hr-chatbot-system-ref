import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { MantineProvider, ColorSchemeScript } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import App from './App';
import { theme } from './theme';

import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ColorSchemeScript defaultColorScheme="light" />
    <MantineProvider theme={theme} defaultColorScheme="light">
      <Notifications position="top-right" />
      <App />
    </MantineProvider>
  </StrictMode>
);
