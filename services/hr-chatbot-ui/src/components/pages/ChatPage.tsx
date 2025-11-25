/**
 * Chat Page Component
 * Main chat interface for interacting with the HR assistant
 */
import React from 'react'
import { Container, Row, Col, Card, Button } from 'react-bootstrap'
import { useAuth } from '../../contexts/AuthContext'
import './ChatPage.css'

const ChatPage: React.FC = () => {
  const { user, logout } = useAuth()

  return (
    <div className="chat-page">
      {/* Header */}
      <div className="chat-header bg-primary text-white p-3 shadow-sm">
        <Container fluid>
          <Row className="align-items-center">
            <Col>
              <h4 className="mb-0">HR Chatbot Assistant</h4>
            </Col>
            <Col xs="auto">
              <div className="d-flex align-items-center gap-3">
                <span>
                  {user?.first_name} {user?.last_name}
                </span>
                <Button variant="outline-light" size="sm" onClick={logout}>
                  Logout
                </Button>
              </div>
            </Col>
          </Row>
        </Container>
      </div>

      {/* Main Content */}
      <Container fluid className="chat-container p-4">
        <Row className="h-100">
          {/* Sidebar - Sessions List */}
          <Col md={3} className="pe-0">
            <Card className="h-100 sidebar-card">
              <Card.Header className="bg-light">
                <div className="d-flex justify-content-between align-items-center">
                  <h6 className="mb-0">Chat History</h6>
                  <Button variant="primary" size="sm">
                    + New Chat
                  </Button>
                </div>
              </Card.Header>
              <Card.Body className="p-2">
                <div className="text-muted text-center py-5">
                  <p>No chat sessions yet</p>
                  <small>Start a new conversation to get started</small>
                </div>
              </Card.Body>
            </Card>
          </Col>

          {/* Main Chat Area */}
          <Col md={9} className="ps-3">
            <Card className="h-100 chat-card">
              <Card.Body className="d-flex flex-column">
                {/* Messages Area */}
                <div className="flex-grow-1 messages-area mb-3">
                  <div className="text-center text-muted py-5">
                    <h5>Welcome to HR Chatbot!</h5>
                    <p>
                      Ask me anything about leaves, attendance, payroll, or HR policies.
                    </p>
                    <div className="mt-4">
                      <p className="fw-bold">Try asking:</p>
                      <ul className="list-unstyled">
                        <li className="mb-2">
                          <Button variant="outline-secondary" size="sm">
                            What's my leave balance?
                          </Button>
                        </li>
                        <li className="mb-2">
                          <Button variant="outline-secondary" size="sm">
                            How do I apply for leave?
                          </Button>
                        </li>
                        <li>
                          <Button variant="outline-secondary" size="sm">
                            Show my recent attendance
                          </Button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Input Area */}
                <div className="input-area">
                  <div className="input-group">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Type your message here..."
                      disabled
                    />
                    <Button variant="primary" disabled>
                      Send
                    </Button>
                  </div>
                  <small className="text-muted d-block mt-2">
                    Chat functionality will be implemented in the next phase
                  </small>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  )
}

export default ChatPage
