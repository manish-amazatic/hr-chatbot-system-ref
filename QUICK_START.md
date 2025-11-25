# Quick Start Guide - Testing Day 1 Implementation

## ✅ What's Been Implemented

**Day 1 tasks completed for**:
- ✅ hr-chatbot-service (Priyanka)
- ✅ hrms-mock-api (Palak)
- ✅ LLMProcessor (Factory + Singleton) - Bonus!

**Total**: 19 Python files, 939 lines of code

---

## 🚀 Start Services Locally

### Option 1: Manual Start (Recommended for Day 1 testing)

#### Terminal 1 - Start HRMS Mock API
```bash
cd /Users/mw/workbench/ai_workshoap/ai_assignment/hr-chatbot-system/services/hrms-mock-api

# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and set:
# JWT_SECRET_KEY=your-secret-key-here

# Start service
python -m api.main
```

Service will start on: **http://localhost:8001**

#### Terminal 2 - Start HR Chatbot Service
```bash
cd /Users/mw/workbench/ai_workshoap/ai_assignment/hr-chatbot-system/services/hr-chatbot-service

# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and set:
# OPENAI_API_KEY=sk-your-key-here
# JWT_SECRET_KEY=your-secret-key-here (same as HRMS)

# Start service
python -m api.main
```

Service will start on: **http://localhost:8000**

---

## 🧪 Test the Implementation

### 1. Test HRMS Health
```bash
curl http://localhost:8001/api/v1/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "HRMS Mock API",
  "version": "1.0.0",
  "timestamp": "2025-01-24T..."
}
```

### 2. Test HRMS Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manish.w@amazatic.com",
    "password": "password123"
  }'
```

**Expected Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "EMP001",
    "email": "manish.w@amazatic.com",
    "first_name": "Manish",
    "last_name": "Wagh",
    "department": "Engineering",
    "designation": "Engineering Manager"
  }
}
```

### 3. Test Chatbot Health
```bash
curl http://localhost:8000/api/v1/health
```

### 4. Test Chatbot Login (forwards to HRMS)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "priyanka.c@amazatic.com",
    "password": "password123"
  }'
```

### 5. Test Chat Endpoint (placeholder)
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my leave balance?",
    "user_id": "EMP001"
  }'
```

---

## 🌐 Access API Documentation

Both services have auto-generated Swagger documentation:

- **HRMS API Docs**: http://localhost:8001/docs
- **Chatbot API Docs**: http://localhost:8000/docs

You can test all endpoints interactively through these UIs!

---

## 👥 Test Users

All users have password: `password123`

| Email | ID | Name | Designation |
|-------|-----|------|-------------|
| manish.w@amazatic.com | EMP001 | Manish Wagh | Engineering Manager |
| priyanka.c@amazatic.com | EMP002 | Priyanka Chavan | Senior Backend Developer |
| palak.s@amazatic.com | EMP003 | Palak Shah | Backend Developer |
| rohit.g@amazatic.com | EMP004 | Rohit Gupta | Frontend Developer |
| manik.l@amazatic.com | EMP005 | Manik Lal | DevOps Engineer |

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # or 8001

# Kill process
kill -9 <PID>
```

### Module Not Found
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

### OPENAI_API_KEY Error
Make sure you've:
1. Created `.env` file from `.env.example`
2. Added your actual OpenAI API key
3. Key starts with `sk-`

---

## 📂 Project Structure (Implemented)

```
hr-chatbot-system/
└── services/
    ├── hr-chatbot-service/        ✅ DONE
    │   ├── api/
    │   │   ├── main.py           ✅ FastAPI app
    │   │   └── routes/
    │   │       ├── health.py     ✅ Health endpoints
    │   │       ├── auth.py       ✅ Auth endpoints
    │   │       └── chat.py       ✅ Chat endpoints
    │   ├── core/
    │   │   └── processors/
    │   │       └── llm_processor.py ✅ Factory + Singleton
    │   └── utils/
    │       └── config.py         ✅ Settings
    │
    └── hrms-mock-api/            ✅ DONE
        ├── api/
        │   ├── main.py           ✅ FastAPI app
        │   └── routes/
        │       ├── health.py     ✅ Health endpoints
        │       └── auth.py       ✅ Auth + 5 mock users
        └── utils/
            ├── config.py         ✅ Settings
            └── jwt_utils.py      ✅ JWT + password hashing
```

---

## 🎯 What Works

### hr-chatbot-service
✅ FastAPI application running
✅ Health check endpoint
✅ Configuration management
✅ Authentication (forwards to HRMS)
✅ Chat endpoints (placeholders)
✅ LLMProcessor (Factory + Singleton)
✅ CORS enabled
✅ Logging configured

### hrms-mock-api
✅ FastAPI application running
✅ Health check endpoint
✅ Configuration management
✅ JWT token creation/verification
✅ Password hashing (bcrypt)
✅ **5 working mock users**
✅ **Full login authentication**
✅ CORS enabled

---

## 📝 Next Steps

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for:
- Detailed implementation summary
- Day 2 tasks
- Statistics and metrics
- Progress tracking

---

*Ready to test! Both backend services are functional.* 🚀
