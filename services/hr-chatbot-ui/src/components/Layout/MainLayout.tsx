import React from 'react';
import Header from './Header';
import SessionList from '../Sidebar/SessionList';
import ChatInterface from '../Chat/ChatInterface';
import ExamplesPanel from '../Examples/ExamplesPanel';
import { useChat } from '../../contexts/ChatContext';

const MainLayout: React.FC = () => {
  const { currentSession } = useChat();

  return (
    <div className="vh-100 d-flex flex-column">
      <Header />
      
      <div className="flex-grow-1 overflow-hidden">
        <div className="row g-0 h-100">
          {/* Left Sidebar - Session List */}
          <div className="col-md-4 col-lg-3 border-end">
            <SessionList />
          </div>

          {/* Right Side - Chat or Examples */}
          <div className="col-md-8 col-lg-9">
            {currentSession ? <ChatInterface /> : <ExamplesPanel />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
