import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from './Header';
import SessionList from '../Sidebar/SessionList';
import ChatInterface from '../Chat/ChatInterface';
import ExamplesPanel from '../Examples/ExamplesPanel';
import { useChat } from '../../contexts/ChatContext';

const MainLayout: React.FC = () => {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();
  const { currentSession, selectSession, setCurrentSession, setMessages } = useChat();

  const handleNewChat = () => {
    // Clear current session and navigate to home
    setCurrentSession(null);
    setMessages([]);
    navigate('/', { replace: true });
  };

  // Sync URL with current session
  useEffect(() => {
    if (sessionId && (!currentSession || currentSession.id !== sessionId)) {
      // Load session from URL parameter
      selectSession(sessionId).catch(() => {
        // If session doesn't exist, redirect to home
        navigate('/', { replace: true });
      });
    }
  }, [sessionId]);

  // Update URL when current session changes
  useEffect(() => {
    if (currentSession && window.location.pathname !== `/chat/${currentSession.id}`) {
      navigate(`/chat/${currentSession.id}`, { replace: true });
    } else if (!currentSession && sessionId) {
      // If no current session but we have a sessionId in URL, go home
      navigate('/', { replace: true });
    }
  }, [currentSession, navigate, sessionId]);

  return (
    <div className=" d-flex flex-column h-100 position-relative">
      <Header />

      <div className="flex-grow-1 d-flex h-100 overflow-auto position-relative">
        <div className="row g-0 h-100 position-relative w-100">
          {/* Left Sidebar - Session List */}
          <div className="col-md-4 col-lg-3 border-end d-flex flex-column h-100 m-0">
            {/* New Chat Button */}
            <div className="p-3 d-flex border-bottom">
              <button
                className="btn btn-primary w-100"
                onClick={handleNewChat}
              >
                <i className="bi bi-plus-circle me-2"></i>
                New Chat
              </button>
            </div>

            <SessionList />
          </div>

          {/* Right Side - Chat or Examples */}
          <div className="col-md-8 col-lg-9 d-flex flex-column h-100 fixed-shrink-1 ">
            {currentSession ? <ChatInterface /> : <ExamplesPanel />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
