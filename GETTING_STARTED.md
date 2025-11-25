# Getting Started with HR Chatbot System

## 🎯 Quick Start (5 minutes)

### Step 1: Prerequisites Check
Ensure you have:
- ✅ Docker & Docker Compose installed
- ✅ Python 3.10+ (for local development)
- ✅ Node.js 18+ (for UI development)
- ✅ OpenAI API Key

### Step 2: Clone & Configure
```bash
cd hr-chatbot-system

# Copy and edit environment file
cp .env.example .env

# Add your OpenAI API key
nano .env  # or your preferred editor
```

**Required in .env**:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
JWT_SECRET_KEY=your-secret-key-here
```

### Step 3: Start Services
```bash
# Make scripts executable
chmod +x infrastructure/scripts/*.sh

# Start all services with Docker Compose
./infrastructure/scripts/start-dev.sh

# Or manually:
docker-compose up --build
```

### Step 4: Access Applications
- **Frontend**: http://localhost:3000
- **Chatbot API Docs**: http://localhost:8000/docs
- **HRMS API Docs**: http://localhost:8001/docs

### Step 5: Login
Use any employee credentials:
- Email: `manish.w@amazatic.com`
- Password: `password123`

---

## 🏗️ For Contributors

### Team Assignments

| Name | Email | Service | Port |
|------|-------|---------|------|
| Manish | manish.w@amazatic.com | Tech Lead | - |
| Priyanka | priyanka.c@amazatic.com | hr-chatbot-service | 8000 |
| Palak | palak.s@amazatic.com | hrms-mock-api | 8001 |
| Rohit | rohit.g@amazatic.com | hr-chatbot-ui | 3000 |
| Manik | manik.l@amazatic.com | DevOps | - |

### Your First Day

#### 1. Read Documentation (30 min)
- [ ] Main [README.md](README.md)
- [ ] [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- [ ] Your service README.md
- [ ] [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

#### 2. Setup Your Service (30 min)

**For hr-chatbot-service (Priyanka)**:
```bash
cd services/hr-chatbot-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with OPENAI_API_KEY
```

**For hrms-mock-api (Palak)**:
```bash
cd services/hrms-mock-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**For hr-chatbot-ui (Rohit)**:
```bash
cd services/hr-chatbot-ui
npm install
cp .env.example .env.local
# Edit .env.local with API URLs
```

**For DevOps (Manik)**:
```bash
# Test Docker setup
docker-compose config
docker-compose up milvus
```

#### 3. Review Reference Code (1 hour)
```bash
# Review the reference implementations
cd ../../refcode/

# RAG basics
cat day1/core/chat_service.py
cat day1/core/milvus_service.py

# Agents & Tools
cat day2/core/agents/orchestrator.py
cat day2/examples/example_3_tools.py
```

#### 4. Start Your First Task (Rest of Day 1)
Open [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) and find your Week 1, Day 1 tasks.

---

## 📅 Development Workflow

### Daily Routine

**Morning (9:00 AM)**:
1. Daily standup (15 min)
   - What did you complete yesterday?
   - What will you work on today?
   - Any blockers?

2. Pull latest changes
   ```bash
   git pull origin main
   ```

**During Day**:
3. Work on assigned tasks
4. Update implementation plan checkboxes
5. Commit frequently
   ```bash
   git add .
   git commit -m "feat: implement leave agent"
   git push
   ```

**End of Day (5:30 PM)**:
6. Update progress in IMPLEMENTATION_PLAN.md
7. Push all changes
8. Note any blockers for standup

### Weekly Milestones

**Week 1**: Foundation & Setup
- All projects initialized
- Dependencies installed
- Basic structure in place
- Milvus and databases setup

**Week 2**: Core Development
- All APIs implemented
- Agents and tools built
- UI components created
- Integration starting

**Week 3**: Integration & Testing
- Services connected
- End-to-end flows working
- Bug fixes
- Testing

**Week 4**: Polish & Demo
- Final testing
- Documentation complete
- Demo prepared
- Deployment ready

---

## 🧪 Testing Your Changes

### Test Individual Service

**Python Services**:
```bash
cd services/hr-chatbot-service
pytest
pytest tests/test_agents.py  # specific file
pytest -v  # verbose
pytest --cov=.  # with coverage
```

**React UI**:
```bash
cd services/hr-chatbot-ui
npm test
npm run test:coverage
```

### Test All Services
```bash
./infrastructure/scripts/test-all.sh
```

### Manual Testing
1. Start all services
2. Login to UI (http://localhost:3000)
3. Test chat flows:
   - Ask policy question (tests RAG)
   - Apply for leave (tests Leave Agent)
   - Check attendance (tests Attendance Agent)
   - View payslip (tests Payroll Agent)

---

## 🐛 Common Issues & Solutions

### Issue 1: Milvus Connection Failed
**Symptom**: "Failed to connect to Milvus"

**Solution**:
```bash
# Check if Milvus is running
docker ps | grep milvus

# Restart Milvus
docker-compose restart milvus

# Wait 30 seconds for startup
sleep 30

# Test connection
docker-compose logs milvus
```

### Issue 2: HRMS Database Empty
**Symptom**: "No employees found"

**Solution**:
```bash
cd services/hrms-mock-api
python scripts/seed_data.py
```

### Issue 3: OpenAI API Rate Limit
**Symptom**: "Rate limit exceeded"

**Solution**:
- Add delays between requests
- Use lower-tier model (gpt-4o-mini instead of gpt-4)
- Implement caching

### Issue 4: Frontend Can't Connect
**Symptom**: "Network Error"

**Solution**:
```bash
# Check .env.local in hr-chatbot-ui
cat services/hr-chatbot-ui/.env.local

# Should have:
# VITE_API_URL=http://localhost:8000
# VITE_HRMS_API_URL=http://localhost:8001

# Check if backend is running
curl http://localhost:8000/api/v1/health
curl http://localhost:8001/api/v1/health
```

### Issue 5: Port Already in Use
**Symptom**: "Address already in use"

**Solution**:
```bash
# Find process using port
lsof -i :8000  # or 8001, 3000

# Kill process
kill -9 <PID>

# Or use different ports in .env
```

---

## 📊 Monitoring Progress

### Check Service Health
```bash
# Check all services
docker-compose ps

# Check specific service
curl http://localhost:8000/api/v1/health
curl http://localhost:8001/api/v1/health
```

### View Logs
```bash
# All services
./infrastructure/scripts/logs.sh all

# Specific service
./infrastructure/scripts/logs.sh hr-chatbot-service
./infrastructure/scripts/logs.sh hrms-mock-api
./infrastructure/scripts/logs.sh hr-chatbot-ui
```

### Track Implementation Progress
Open [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) and check:
- [ ] Boxes for completed tasks
- Your current week/day section
- Upcoming tasks

---

## 🎓 Learning Resources

### Internal Documentation
1. [README.md](README.md) - Project overview
2. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Detailed tasks
3. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File organization
4. Service READMEs - Service-specific docs

### External Resources
- **LangChain**: https://python.langchain.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **assistant-ui**: https://github.com/assistant-ui/assistant-ui
- **Milvus**: https://milvus.io/docs
- **React**: https://react.dev/

### Reference Code
- `refcode/day1/` - RAG basics, Milvus, FAISS
- `refcode/day2/` - Agents, Tools, Memory

---

## 🚀 Deployment Commands

### Start Everything
```bash
./infrastructure/scripts/start-dev.sh
```

### Stop Everything
```bash
./infrastructure/scripts/stop-all.sh
```

### Reset Databases
```bash
./infrastructure/scripts/reset-db.sh
```

### View Logs
```bash
./infrastructure/scripts/logs.sh [service_name]
```

### Run Tests
```bash
./infrastructure/scripts/test-all.sh
```

---

## 📞 Getting Help

### Daily Standup
- Time: 9:00 AM daily
- Format: 15 minutes
- Share: Progress, plans, blockers

### Tech Lead
- **Name**: Manish (manish.w@amazatic.com)
- **For**: Architecture questions, technical decisions

### Slack/Teams
- Channel: #hr-chatbot-dev
- Post: Questions, blockers, updates

### GitHub Issues
- Create issues for:
  - Bugs
  - Feature requests
  - Documentation improvements

---

## ✅ Definition of Done

Before marking a task complete, ensure:
- [ ] Code written and tested
- [ ] Unit tests added (if applicable)
- [ ] Documentation updated
- [ ] Code committed and pushed
- [ ] Checkbox in IMPLEMENTATION_PLAN.md checked
- [ ] No breaking changes to other services

---

## 🎉 Ready to Start!

You're all set! Follow these steps:

1. ✅ Read this document
2. ✅ Setup your environment
3. ✅ Review reference code
4. ✅ Start Day 1 tasks in IMPLEMENTATION_PLAN.md
5. ✅ Attend daily standup
6. ✅ Have fun building! 🚀

---

*Questions? Check documentation or ask in #hr-chatbot-dev*
*Last Updated: 2025-01-24*
