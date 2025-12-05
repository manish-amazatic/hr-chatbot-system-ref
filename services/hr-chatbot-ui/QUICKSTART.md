# HR Chatbot UI - Quick Start Guide

## 🚀 Getting Started

### Option 1: Local Development (Recommended for testing)

1. **Install dependencies**:
   ```bash
   cd services/hr-chatbot-ui
   npm install
   ```

2. **Configure environment** (already created):
   ```bash
   # .env file is ready with:
   VITE_API_BASE_URL=http://localhost:8000
   VITE_USER_ID=EMP001
   ```

3. **Start the backend service first** (in another terminal):
   ```bash
   cd services/hr-chatbot-service
   # Follow backend setup instructions
   ```

4. **Start the UI**:
   ```bash
   npm run dev
   ```

5. **Open browser**: Navigate to http://localhost:3000

### Option 2: Docker (Full Stack)

1. **Start all services**:
   ```bash
   # From project root
   docker-compose up
   ```

2. **Access the UI**: http://localhost:3000

## 🎯 Features to Test

### 1. Quick Prompts (Left Sidebar)
- Click on any category to expand/collapse
- All categories are expanded by default
- Click any prompt button to auto-fill the chat input

### 2. Chat Interface
- Type messages in the input field at the bottom
- Press Enter to send
- Watch messages stream in real-time
- See agent badges on assistant responses

### 3. Dark/Light Mode
- Click the sun/moon icon in the header (top right)
- Toggle between themes

### 4. User ID Display
- Your user ID (EMP001) is shown in the header
- This is used for all API calls

### 5. Connection Status
- Green badge = Connected
- Yellow badge = Connecting
- Red badge = Error
- Click "Retry" button if disconnected

## 📋 Example Prompts to Try

### Leave Management
- "What's my current leave balance?"
- "I want to apply for 3 days of annual leave from December 20th to December 22nd"
- "Show me my leave history for this year"

### Attendance
- "Give me my attendance summary for this month"
- "What time did I check in today?"
- "Show my attendance records for November"

### Payroll
- "Show me my latest payslip"
- "What's my year-to-date salary?"
- "Explain my PF deduction"

### HR Policies
- "Tell me about the remote work policy"
- "What are the public holidays in 2025?"
- "What health benefits do employees get?"

## 🔧 Troubleshooting

### UI won't load
- Check that port 3000 is not in use
- Ensure all dependencies are installed: `npm install`

### Can't connect to backend
- Verify backend is running on port 8000
- Check .env file has correct VITE_API_BASE_URL
- Look for connection status in header

### Prompts not loading
- Check browser console for errors
- Verify `src/config/prompts.json` is valid JSON
- Restart dev server: `npm run dev`

### Build fails
- Delete node_modules and package-lock.json
- Run `npm install` again
- Check for TypeScript errors: `npm run build`

## 📝 Customization

### Change User ID
Edit `.env`:
```bash
VITE_USER_ID=YOUR_EMPLOYEE_ID
```

### Add More Prompts
Edit `src/config/prompts.json`:
```json
{
  "name": "Your Category",
  "icon": "IconName",
  "prompts": [
    {
      "id": "unique-id",
      "label": "Button Text",
      "prompt": "Message to send"
    }
  ]
}
```

### Modify Theme
Edit `src/theme.ts` to change colors, fonts, spacing, etc.

## 🎨 UI Features

✅ Responsive design (works on mobile)
✅ Keyboard navigation (Tab through elements)
✅ Screen reader support
✅ Auto-scroll to latest message
✅ Typing indicator while streaming
✅ Agent identification badges
✅ Error handling with retry
✅ Session-only chat (no persistence)

## 🐛 Known Limitations

- Chat history is session-only (cleared on refresh)
- No message editing or deletion
- No file upload support
- No multi-user chat (single user per session)

## 📦 Production Deployment

```bash
# Build for production
npm run build

# Serve with nginx or similar
# Built files are in dist/
```

## 🆘 Need Help?

- Check README.md for full documentation
- Review backend API documentation
- Inspect browser console for errors
- Check terminal for server errors
