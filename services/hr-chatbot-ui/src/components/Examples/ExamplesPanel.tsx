import React, { useState } from 'react';
import { useChat } from '../../contexts/ChatContext';

interface ExamplePrompt {
  text: string;
  icon: string;
  category: string;
}

const examples: ExamplePrompt[] = [
  // Leave Management
  { text: "What's my current leave balance?", icon: 'calendar-check', category: 'Leave' },
  { text: "Apply for 2 days sick leave from tomorrow", icon: 'calendar-plus', category: 'Leave' },
  { text: "Show my leave request history", icon: 'clock-history', category: 'Leave' },
  { text: "What is the maternity leave policy?", icon: 'book', category: 'Leave' },
  
  // Attendance
  { text: "Show my attendance summary for this month", icon: 'clipboard-check', category: 'Attendance' },
  { text: "Mark my attendance for today", icon: 'check-circle', category: 'Attendance' },
  { text: "What are the working hours?", icon: 'clock', category: 'Attendance' },
  
  // Payroll
  { text: "Show my latest salary slip", icon: 'currency-dollar', category: 'Payroll' },
  { text: "What's my year-to-date gross salary?", icon: 'graph-up', category: 'Payroll' },
  { text: "Explain the salary components", icon: 'list-ul', category: 'Payroll' },
  
  // HR Policies
  { text: "What is the work from home policy?", icon: 'house', category: 'Policies' },
  { text: "Explain the performance review process", icon: 'star', category: 'Policies' },
  { text: "What are the company holidays?", icon: 'calendar3', category: 'Policies' },
  { text: "Tell me about the code of conduct", icon: 'shield-check', category: 'Policies' },
];

const ExamplesPanel: React.FC = () => {
  const { createSession, sendMessage } = useChat();
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleExampleClick = async (text: string) => {
    await createSession();
    await sendMessage(text);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    setIsSending(true);
    try {
      await createSession();
      await sendMessage(inputMessage.trim());
      setInputMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const groupedExamples = examples.reduce((acc, example) => {
    if (!acc[example.category]) {
      acc[example.category] = [];
    }
    acc[example.category].push(example);
    return acc;
  }, {} as Record<string, ExamplePrompt[]>);

  return (
    <div className="h-100 d-flex flex-column">
      <div className="flex-grow-1 overflow-auto">
        <div className="container py-5">
          {/* Header */}
          <div className="text-center mb-5">
            <h1 className="display-4 mb-3">
              <i className="bi bi-robot me-3"></i>
              Welcome to HR Chatbot
            </h1>
            <p className="lead text-muted">
              Your intelligent HR assistant. Ask me anything about policies, leave, attendance, or payroll.
            </p>
          </div>

          {/* Message Input */}
          <div className="row mb-5">
            <div className="col-lg-8 mx-auto">
              <div className="card shadow-sm">
                <div className="card-body">
                  <form onSubmit={handleSendMessage}>
                    <div className="input-group input-group-lg">
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Type your message to start a new chat..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        disabled={isSending}
                      />
                      <button
                        className="btn btn-primary"
                        type="submit"
                        disabled={!inputMessage.trim() || isSending}
                      >
                        {isSending ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            Sending...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-send-fill me-2"></i>
                            Send
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>

        {/* Example Prompts */}
        <div className="row g-4">
          {Object.entries(groupedExamples).map(([category, prompts]) => (
            <div key={category} className="col-md-6">
              <div className="card h-100 shadow-sm">
                <div className="card-header bg-primary text-white">
                  <h5 className="mb-0">
                    <i className="bi bi-lightbulb me-2"></i>
                    {category}
                  </h5>
                </div>
                <div className="card-body">
                  <div className="d-grid gap-2">
                    {prompts.map((prompt, idx) => (
                      <button
                        key={idx}
                        className="btn btn-outline-primary text-start"
                        onClick={() => handleExampleClick(prompt.text)}
                      >
                        <i className={`bi bi-${prompt.icon} me-2`}></i>
                        {prompt.text}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Features */}
        <div className="row mt-5">
          <div className="col-12">
            <h3 className="text-center mb-4">What I Can Help You With</h3>
          </div>
          <div className="col-md-3">
            <div className="text-center p-3">
              <i className="bi bi-calendar-check fs-1 text-primary"></i>
              <h5 className="mt-2">Leave Management</h5>
              <p className="text-muted small">Check balance, apply, view history</p>
            </div>
          </div>
          <div className="col-md-3">
            <div className="text-center p-3">
              <i className="bi bi-clock-history fs-1 text-success"></i>
              <h5 className="mt-2">Attendance</h5>
              <p className="text-muted small">Track attendance, view reports</p>
            </div>
          </div>
          <div className="col-md-3">
            <div className="text-center p-3">
              <i className="bi bi-currency-dollar fs-1 text-warning"></i>
              <h5 className="mt-2">Payroll</h5>
              <p className="text-muted small">Salary slips, YTD earnings</p>
            </div>
          </div>
          <div className="col-md-3">
            <div className="text-center p-3">
              <i className="bi bi-book fs-1 text-info"></i>
              <h5 className="mt-2">HR Policies</h5>
              <p className="text-muted small">Search and understand policies</p>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default ExamplesPanel;
