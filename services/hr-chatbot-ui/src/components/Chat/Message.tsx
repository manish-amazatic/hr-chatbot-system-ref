import React from 'react';
import { Message as MessageType } from '../../types/chat.types';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user' || (message as any).type === 'human';

  return (
    <div className={`mb-4 ${isUser ? 'text-end' : ''}`}>
      <div className={`d-inline-block text-start ${isUser ? 'bg-primary text-white' : 'bg-light'} rounded p-3`} style={{ maxWidth: '80%' }}>
        {/* Message Header */}
        <div className="d-flex align-items-center mb-2">
          <i className={`bi ${isUser ? 'bi-person-fill' : 'bi-robot'} me-2`}></i>
          <strong>{isUser ? 'You' : 'HR Assistant'}</strong>
          {message.agentUsed && (
            <span className="badge bg-secondary ms-2 small">
              {message.agentUsed}
            </span>
          )}
        </div>

        {/* Message Content */}
        <div style={{ whiteSpace: 'pre-wrap' }}>
          {message.content}
        </div>

        {/* Sources (if any) */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-top">
            <small className="text-muted d-block mb-2">
              <i className="bi bi-book me-1"></i>
              Sources:
            </small>
            {message.sources.map((source, idx) => (
              <div key={idx} className="small mb-1">
                <span className="badge bg-info me-1">{source.score.toFixed(2)}</span>
                {source.metadata?.source || source.documentId}
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className="text-end mt-2">
          <small className={isUser ? 'text-white-50' : 'text-muted'}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </small>
        </div>
      </div>
    </div>
  );
};

export default Message;
