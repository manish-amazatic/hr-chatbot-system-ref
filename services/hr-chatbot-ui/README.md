# HR Chatbot UI

Modern and professional HR Chatbot user interface built with React, TypeScript, Vite, and Mantine UI.

## Features

- 🎨 **Modern UI**: Clean, professional design using Mantine v7 component library
- 🌓 **Dark/Light Mode**: Toggle between color schemes for comfortable viewing
- 💬 **Streaming Chat**: Real-time message streaming using Server-Sent Events (SSE)
- 📋 **Quick Prompts**: Pre-configured prompts organized in expandable categories:
  - Leave Management (6 prompts)
  - Attendance Tracking (6 prompts)
  - Payroll & Compensation (7 prompts)
  - HR Policies & Benefits (7 prompts)
- 🤖 **Agent Identification**: Visual badges showing which agent handled each query
- ♿ **Accessibility**: Full keyboard navigation, ARIA labels, and screen reader support
- 🔌 **Connection Status**: Real-time connection monitoring with auto-retry
- 👤 **User Display**: Shows current user ID from environment configuration

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite 6** - Build tool and dev server
- **Mantine v7** - Component library
- **Tabler Icons** - Icon set

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_USER_ID=EMP001
```

### Development

```bash
# Start development server
npm run dev

# Access at http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Docker

### Development Mode

```bash
# Build and run with docker-compose
docker-compose up hr-chatbot-ui

# Access at http://localhost:3000
```

### Production Mode

```bash
# Build production image
docker build -t hr-chatbot-ui:prod --target production .

# Run production container
docker run -p 80:80 hr-chatbot-ui:prod
```

## Project Structure

```
src/
├── components/          # React components
│   ├── ChatInterface.tsx    # Main chat interface
│   ├── MessageBubble.tsx    # Message display component
│   ├── Sidebar.tsx          # Sidebar with prompts
│   ├── Header.tsx           # Header with user info
│   ├── PromptCard.tsx       # Individual prompt button
│   └── ErrorBanner.tsx      # Error notification
├── contexts/           # React contexts
│   └── ChatContext.tsx      # Chat state management
├── services/           # API services
│   └── chatApi.ts           # Chat API client
├── types/              # TypeScript types
│   ├── chat.ts              # Chat-related types
│   └── prompts.ts           # Prompt types
├── config/             # Configuration
│   └── prompts.json         # Prompt definitions
├── utils/              # Utility functions
│   ├── agentHelpers.ts      # Agent display utilities
│   └── promptLoader.ts      # Prompt loading
├── theme.ts            # Mantine theme configuration
├── App.tsx             # Root component
├── main.tsx            # Entry point
└── vite-env.d.ts       # Vite type definitions
```

## Configuration

### Environment Variables

- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)
- `VITE_USER_ID`: User identifier (default: EMP001)

### Adding Prompts

Edit `src/config/prompts.json` to add or modify prompt categories and prompts:

```json
{
  "name": "Category Name",
  "icon": "IconName",
  "prompts": [
    {
      "id": "unique-id",
      "label": "Display Label",
      "prompt": "Actual prompt text to send"
    }
  ]
}
```

### Theme Customization

Edit `src/theme.ts` to customize colors, fonts, and component defaults.

## API Integration

The UI connects to the HR Chatbot Service backend via:

- **Streaming Endpoint**: `POST /api/v1/chat/message/stream`
- **Health Check**: `GET /api/v1/health`

## Accessibility Features

- Full keyboard navigation support
- ARIA labels on all interactive elements
- Screen reader compatible
- Focus indicators
- Live regions for chat updates
- Color contrast meeting WCAG 2.1 AA standards

## Agent Badge Colors

- 🟢 **Leave Agent** - Green
- 🔵 **Attendance Agent** - Blue  
- 🟠 **Payroll Agent** - Orange
- 🟣 **HR Policy** - Purple

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## License

Part of the HR Chatbot System Reference Implementation
