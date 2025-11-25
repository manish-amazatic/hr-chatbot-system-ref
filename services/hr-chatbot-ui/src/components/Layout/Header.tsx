import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light border-bottom">
      <div className="container-fluid">
        <span className="navbar-brand mb-0 h1">
          <i className="bi bi-robot me-2"></i>
          HR Chatbot
        </span>

        <div className="d-flex align-items-center">
          <span className="me-3">
            <i className="bi bi-person-circle me-2"></i>
            {user?.firstName} {user?.lastName}
          </span>
          <button className="btn btn-outline-danger btn-sm" onClick={logout}>
            <i className="bi bi-box-arrow-right me-1"></i>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Header;
