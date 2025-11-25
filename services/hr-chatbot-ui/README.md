# HR Chatbot UI

Modern, responsive web interface for the HR chatbot with employee login, chat interface with session management, and example prompts section.

## Owner
**rohit.g@amazatic.com**

## Tech Stack
- React 18+ with TypeScript
- Vite (Build Tool)
- Bootstrap 5
- assistant-ui (Chat Interface)
- React Router v6
- Axios (HTTP Client)

## Features

- Split-screen layout (50-50)
- Employee authentication
- Chat interface with assistant-ui
- Session management
- Example prompts panel
- Responsive design
- Source citations display

## Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env.local
# Edit .env.local and set API URLs
```

**`.env.local`**:
```
VITE_API_URL=http://localhost:8000
VITE_HRMS_API_URL=http://localhost:8001
```

### 3. Run Development Server
```bash
npm run dev
```

Visit: http://localhost:5173

## Build for Production

```bash
npm run build
npm run preview
```

## Testing

```bash
npm test
```

## Project Structure

```
hr-chatbot-ui/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── Chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── Message.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── Sidebar/
│   │   │   ├── SessionList.tsx
│   │   │   └── SessionItem.tsx
│   │   ├── Examples/
│   │   │   ├── ExamplesPanel.tsx
│   │   │   └── PromptCard.tsx
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── MainLayout.tsx
│   ├── contexts/
│   │   ├── AuthContext.tsx        # Authentication state
│   │   └── ChatContext.tsx        # Chat state management
│   ├── services/
│   │   ├── api.ts                 # Axios instance
│   │   ├── authService.ts         # Auth API calls
│   │   └── chatService.ts         # Chat API calls
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   └── useSessions.ts
│   ├── types/
│   │   ├── auth.types.ts
│   │   ├── chat.types.ts
│   │   └── session.types.ts
│   ├── utils/
│   │   ├── tokenManager.ts
│   │   └── formatters.ts
│   ├── assets/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
└── README.md
```

## Default Credentials

For testing, use any employee from HRMS:
- Email: `manish.w@amazatic.com`
- Password: `password123`

## Implementation Tasks

See [IMPLEMENTATION_PLAN.md](../../IMPLEMENTATION_PLAN.md) for detailed tasks.
