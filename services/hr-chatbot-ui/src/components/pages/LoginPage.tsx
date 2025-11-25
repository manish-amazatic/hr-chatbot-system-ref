/**
 * Login Page Component
 * Allows users to authenticate with email and password
 */
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Card, Form, Button, Alert } from 'react-bootstrap'
import { useAuth } from '../../contexts/AuthContext'
import './LoginPage.css'

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat')
    }
  }, [isAuthenticated, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(email, password)
      // Navigation handled by AuthContext
    } catch (err: any) {
      console.error('Login error:', err)
      setError(
        err.response?.data?.detail || 'Login failed. Please check your credentials.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <Container className="d-flex justify-content-center align-items-center min-vh-100">
        <Card className="login-card shadow">
          <Card.Body className="p-5">
            <div className="text-center mb-4">
              <h2 className="mb-2">HR Chatbot</h2>
              <p className="text-muted">Sign in to access your HR assistant</p>
            </div>

            {error && (
              <Alert variant="danger" dismissible onClose={() => setError('')}>
                {error}
              </Alert>
            )}

            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3" controlId="email">
                <Form.Label>Email</Form.Label>
                <Form.Control
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  disabled={isLoading}
                />
              </Form.Group>

              <Form.Group className="mb-4" controlId="password">
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  disabled={isLoading}
                />
              </Form.Group>

              <Button
                variant="primary"
                type="submit"
                className="w-100"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <span
                      className="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </Form>

            <div className="mt-4 text-center text-muted">
              <small>
                <strong>Demo Credentials:</strong>
                <br />
                Email: manish.w@amazatic.com
                <br />
                Password: password123
              </small>
            </div>
          </Card.Body>
        </Card>
      </Container>
    </div>
  )
}

export default LoginPage
