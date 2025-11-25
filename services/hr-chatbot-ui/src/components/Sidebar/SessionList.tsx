import React from 'react';
import { useChat } from '../../contexts/ChatContext';

const SessionList: React.FC = () => {
  const { sessions, currentSession, createSession, selectSession, deleteSession } = useChat();

  const handleDelete = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this session?')) {
      try {
        await deleteSession(sessionId);
      } catch (error) {
        console.error('Failed to delete session:', error);
      }
    }
  };

  return (
    <div className="d-flex flex-column h-100">
      {/* New Chat Button */}
      <div className="p-3 border-bottom">
        <button
          className="btn btn-primary w-100"
          onClick={createSession}
        >
          <i className="bi bi-plus-circle me-2"></i>
          New Chat
        </button>
      </div>

      {/* Session List */}
      <div className="flex-grow-1 overflow-auto">
        {sessions.length === 0 ? (
          <div className="text-center text-muted p-4">
            <i className="bi bi-chat-dots fs-1 d-block mb-2"></i>
            <p>No chat sessions yet</p>
            <p className="small">Start a new conversation!</p>
          </div>
        ) : (
          <div className="list-group list-group-flush">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`list-group-item list-group-item-action cursor-pointer ${
                  currentSession?.id === session.id ? 'active' : ''
                }`}
                onClick={() => selectSession(session.id)}
                style={{ cursor: 'pointer' }}
              >
                <div className="d-flex justify-content-between align-items-start">
                  <div className="flex-grow-1">
                    <h6 className="mb-1">
                      {session.title || 'New Chat'}
                    </h6>
                    <small className="text-muted">
                      {new Date(session.createdAt).toLocaleDateString()}
                    </small>
                  </div>
                  <button
                    className="btn btn-sm btn-link text-danger p-0"
                    onClick={(e) => handleDelete(session.id, e)}
                    title="Delete session"
                  >
                    <i className="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionList;
