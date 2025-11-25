import React, { useState } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="input-group">
        <textarea
          className="form-control"
          placeholder="Ask me anything about HR policies, leave, attendance, payroll..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={3}
          style={{ resize: 'none' }}
        />
        <button
          className="btn btn-primary"
          type="submit"
          disabled={disabled || !message.trim()}
        >
          {disabled ? (
            <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          ) : (
            <i className="bi bi-send-fill"></i>
          )}
        </button>
      </div>
      <small className="text-muted">Press Enter to send, Shift+Enter for new line</small>
    </form>
  );
};

export default MessageInput;
