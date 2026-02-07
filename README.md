# AIAgency - Multi-Agent Orchestration System

A FastAPI-based multi-agent system that orchestrates specialized AI agents (Legal, Research, and Manager) to handle complex tasks through intelligent delegation and collaboration. The system uses Pydantic-AI for agent management, Celery for asynchronous task processing, and provides a RESTful API with JWT authentication.

## 🎯 Features

- **Multi-Agent Orchestration**: Manager agent intelligently delegates tasks to specialized agents
- **Specialized Agents**:
  - **Legal Agent**: Handles legal matters, contracts, compliance, and regulatory frameworks with PDF generation
  - **Research Agent**: Conducts web research using DuckDuckGo and synthesizes findings
  - **Manager Agent**: Coordinates tasks, strategic planning, and quality assurance
- **Asynchronous Task Processing**: Celery + Redis for background job execution
- **Authentication & Authorization**: JWT-based authentication with role-based access control
- **Rate Limiting**: Request throttling using SlowAPI
- **PDF Generation**: Legal document generation using WeasyPrint
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Database**: SQLAlchemy with SQLite (easily swappable to PostgreSQL/MySQL)

## 📋 Prerequisites

- Python 3.12 or higher
- Redis server (for Celery broker/backend)
- Git (for cloning the repository)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd AIAgency
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start Redis

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**On macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**On Windows:**
Download Redis from https://github.com/microsoftarchive/redis/releases or use WSL

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following environment variables to `.env`:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# JWT Security Settings
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin User Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
ADMIN_EMAIL=admin@example.com
```

**To generate a secure SECRET_KEY:**
```bash
python main.py
# Or use:
python -c "from secrets import token_urlsafe; print(token_urlsafe(32))"
```

**To get an OpenRouter API Key:**
1. Visit https://openrouter.ai/
2. Sign up for an account
3. Navigate to API Keys section
4. Generate a new API key

## 🏃 Running the Application

You need to run **three** separate processes:

### Terminal 1: Start the FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

### Terminal 2: Start the Celery Worker

```bash
celery -A app.tasks.tasks worker --loglevel=info
```

### Terminal 3: (Optional) Monitor Celery Tasks

```bash
celery -A app.tasks.tasks flower
```

Access Flower dashboard at http://localhost:5555

## 📚 Project Structure

```
AIAgency/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── agents/                 # AI Agent implementations
│   │   ├── base.py            # Base agent class
│   │   ├── manager.py         # Agent orchestrator
│   │   ├── specialized_agents.py  # Legal, Research, Manager agents
│   │   ├── schemas/           # Agent-specific schemas
│   │   └── tools/             # Agent tools (PDF, search)
│   ├── api/                   # API routes
│   │   ├── deps.py           # Dependencies (DB sessions)
│   │   └── v1/               # API version 1
│   │       ├── router.py     # Main API router
│   │       └── auth/         # Authentication endpoints
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database setup
│   │   ├── limiter.py        # Rate limiting
│   │   ├── logging.py        # Logging configuration
│   │   └── security.py       # JWT & security
│   ├── enums/                 # Enumerations
│   │   ├── files.py
│   │   ├── messages.py
│   │   ├── subscription.py
│   │   ├── task_status.py
│   │   └── users.py
│   ├── models/                # SQLAlchemy models
│   │   ├── agent_tasks.py
│   │   ├── generated_files.py
│   │   ├── messages.py
│   │   └── users.py
│   ├── prompts/               # System prompts for agents
│   │   ├── legal_agent.txt
│   │   ├── manager_agent.txt
│   │   ├── project_agent.txt
│   │   └── research_agent.txt
│   ├── schemas/               # Pydantic schemas
│   │   ├── agent_task.py
│   │   └── token.py
│   ├── scripts/               # Utility scripts
│   │   ├── admin.py          # Admin user creation
│   │   └── hashing.py        # Password hashing
│   ├── services/              # Business logic services
│   └── tasks/                 # Celery tasks
│       └── tasks.py
├── output/                    # Generated files output
├── templates/                 # HTML templates
│   └── legal_template.html
├── main.py                    # Secret key generator
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata
└── README.md                 # This file
```

## 🔌 API Endpoints

### Authentication

**POST** `/api/v1/auth/login`
- Login with username and password
- Returns JWT access token

**GET** `/api/v1/auth/me`
- Get current user information
- Requires authentication

### Agent Tasks

**POST** `/run-agent`
- Submit a task to the agent orchestrator
- Request body: `{"prompt": "your task description"}`
- Returns: `{"task_id": "celery-task-id"}`
- Rate limit: 5 requests/minute
- Requires authentication

**GET** `/tasks/{task_id}`
- Get task status and result
- Returns task status: `PENDING`, `RUNNING`, `COMPLETED`, or `FAILED`
- Rate limit: 5 requests/minute
- Requires authentication

### Health Check

**GET** `/health`
- Check API health status
- Rate limit: 5 requests/minute

## 🔐 Authentication Flow

1. **Login** to get access token:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

2. **Use token** in subsequent requests:
```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Research the latest AI trends"}'
```

## 🧪 Example Usage

### Submit a Research Task

```bash
# 1. Login and get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password" | jq -r '.access_token')

# 2. Submit task
TASK_ID=$(curl -X POST "http://localhost:8000/run-agent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Research quantum computing advances in 2026"}' | jq -r '.task_id')

# 3. Check task status
curl -X GET "http://localhost:8000/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Submit a Legal Task

```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Draft a software licensing agreement for an open-source project"}'
```

## 🛠️ Development

### Database Migrations

The application automatically creates database tables on startup. To reset the database:

```bash
rm test.db
# Restart the application
```

### Adding New Agents

1. Create agent class in `app/agents/specialized_agents.py`
2. Create system prompt in `app/prompts/`
3. Register agent in `app/agents/manager.py` orchestrator
4. Add agent-specific tools if needed in `app/agents/tools/`

### Customizing System Prompts

Edit the prompt files in `app/prompts/` to customize agent behavior:
- `manager_agent.txt` - Manager orchestration logic
- `legal_agent.txt` - Legal expertise and document generation
- `research_agent.txt` - Research methodology and synthesis
- `project_agent.txt` - Project management capabilities

## 🐛 Troubleshooting

### Redis Connection Error
```
Error: Cannot connect to Redis
```
**Solution:** Ensure Redis is running: `redis-cli ping`

### OpenRouter API Error
```
Error: Invalid API key
```
**Solution:** Verify `OPENROUTER_API_KEY` in `.env` file

### Celery Worker Not Processing Tasks
**Solution:** 
1. Check Redis is running
2. Restart Celery worker
3. Check Celery logs for errors

### Database Locked Error
**Solution:** Ensure only one instance of the application is running, or switch to PostgreSQL for concurrent access

### Import Errors
**Solution:** Ensure virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

## 📝 Configuration Options

### Changing the Database

To use PostgreSQL instead of SQLite, update `app/core/database.py`:

```python
SQLALCHEMY_DATABASE_URL = 'postgresql://user:password@localhost/dbname'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
```

### Changing AI Model Provider

Update model names in `app/agents/specialized_agents.py`:

```python
model_name="openrouter/anthropic/claude-3.5-sonnet"  # Example
```

### Adjusting Rate Limits

Modify rate limits in `app/main.py`:

```python
@limiter.limit("10/minute")  # Changed from 5/minute
```

## 🔒 Security Considerations

- Always use strong passwords for admin account
- Keep `SECRET_KEY` secure and never commit to version control
- Use HTTPS in production
- Rotate API keys regularly
- Consider implementing refresh tokens for long sessions
- Use environment-specific `.env` files
- Enable CORS only for trusted domains in production

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker (create Dockerfile)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

- Use proper database (PostgreSQL/MySQL)
- Set `ACCESS_TOKEN_EXPIRE_MINUTES` appropriately
- Use Redis with authentication
- Configure proper CORS origins
- Enable HTTPS/TLS

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Support

[Add contact/support information here]

---

**Note**: This is an AI-powered application. Ensure you comply with OpenRouter's terms of service and usage policies. Generated content should be reviewed by appropriate professionals before use in production scenarios.