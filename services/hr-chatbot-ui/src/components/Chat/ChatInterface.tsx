import React from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { useChat } from '../../contexts/ChatContext';

const ChatInterface: React.FC = () => {
  const { messages, sendMessage, isLoading } = useChat();

  const handleSendMessage = async (message: string) => {
    try {
      await sendMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <div className="d-flex flex-column h-100">
      {/* Messages */}
      <div className="flex-grow-1 overflow-auto">
        <MessageList messages={messages} />
      </div>

      {/* Input */}
      <div className="border-top p-3">
        <MessageInput onSend={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
};

export default ChatInterface;
