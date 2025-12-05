import { AppShell, Burger } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { ChatProvider, useChatContext } from './contexts/ChatContext';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { ErrorBanner } from './components/ErrorBanner';

const AppContent = () => {
  const [sidebarOpened, { toggle }] = useDisclosure(true);
  const { connectionStatus, sendMessage, reconnect } = useChatContext();

  const handlePromptSelect = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 320,
        breakpoint: 'sm',
        collapsed: { mobile: !sidebarOpened, desktop: !sidebarOpened },
      }}
      padding="0"
    >
      <AppShell.Header>
        <Header connectionStatus={connectionStatus} />
      </AppShell.Header>

      <AppShell.Navbar>
        <Sidebar onPromptSelect={handlePromptSelect} />
      </AppShell.Navbar>

      <AppShell.Main style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <Burger
          opened={sidebarOpened}
          onClick={toggle}
          hiddenFrom="sm"
          size="sm"
          style={{ position: 'absolute', top: 16, left: 16, zIndex: 100 }}
          aria-label="Toggle sidebar"
        />
        
        {connectionStatus === 'error' || connectionStatus === 'disconnected' ? (
          <ErrorBanner onRetry={reconnect} />
        ) : null}
        
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', paddingTop: '60px' }}>
          <ChatInterface />
        </div>
      </AppShell.Main>
    </AppShell>
  );
};

function App() {
  return (
    <ChatProvider>
      <AppContent />
    </ChatProvider>
  );
}

export default App;
