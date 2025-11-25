import React from 'react';
import { Message as MessageType } from '../../types/chat.types';
import Message from './Message';

interface MessageListProps {
  messages: MessageType[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="d-flex justify-content-center align-items-center h-100">
        <div className="text-center text-muted">
          <i className="bi bi-chat-text fs-1 d-block mb-3"></i>
          <h5>Start a conversation</h5>
          <p>Ask me about leave policies, attendance, payroll, or anything HR-related!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
