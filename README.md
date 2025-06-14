# 🤖 FastAPI Agent Backend

A production-ready FastAPI backend that orchestrates multiple AI agents with secure authentication, database persistence, and comprehensive monitoring.

## 🚀 Features

- **🎭 Multi-Agent AI Orchestration**: Support for PraisonAI, CrewAI, and AG2/AutoGen frameworks
- **🔐 Secure Authentication**: Clerk JWT-based user authentication with RS256 verification
- **🗄️ Database Persistence**: Supabase PostgreSQL with SQLAlchemy ORM for session and execution tracking
- **📊 Comprehensive Monitoring**: Prometheus metrics with Grafana dashboards
- **🐳 Docker Ready**: Multi-stage builds with production optimizations
- **☁️ Coolify Deployment**: Pre-configured for seamless Coolify deployment
- **⚡ High Performance**: Async operations with connection pooling and health checks
- **🧪 Testing**: Unit tests and k6 load testing (targeting 20 RPS)
- **🧠 MindsDB Integration**: Connect to MindsDB for machine learning capabilities
- **📧 Gmail Integration**: Send emails and access Gmail data through Google API
- **⚙️ Admin Control Panel**: Streamlit-based UI for easy configuration and setup
- **🖥️ Tauri Integration**: Connect to Tauri desktop applications with secure CORS configuration
- **🔌 Enhanced Supabase Connection**: Direct connection and connection pooling for better performance

## 🏗️ Architecture

```
Internet → Traefik (HTTPS) → FastAPI Backend → AI Agents (PraisonAI/CrewAI/AG2)
                                    ↓
                               Supabase Database
                                    ↓
                            Prometheus → Grafana
                                    ↕
                          MindsDB ← → Gmail API
```

### Core Components

- **FastAPI Application** (`app/main.py`) - Main entry point with middleware configuration
- **AI Agent Orchestrator** (`app/agents.py`) - Multi-agent system with graceful fallback
- **Authentication Layer** (`app/auth.py`) - Clerk JWT verification and user management
- **Database Layer** (`app/database.py`) - Async SQLAlchemy with Supabase backend
- **Monitoring System** (`app/monitoring.py`) - Prometheus metrics and structured logging
- **MindsDB Integration** (`app/integrations/mindsdb.py`) - Machine learning capabilities
- **Gmail Integration** (`app/integrations/gmail.py`) - Email and Gmail data access

## 🎯 API Endpoints

- `POST /v1/answer` - Execute AI agent tasks
- `POST /v1/sessions` - Create conversation sessions
- `GET /v1/agents` - List available agents
- `GET /v1/health` - Health check endpoint
- `GET /metrics` - Prometheus metrics (restricted)

## 🛠️ Supported AI Agents

1. **PraisonAI** (`praisonai`) - Multi-agent orchestration with structured outputs
2. **CrewAI** (`crewai`) - Collaborative AI agents for complex tasks  
3. **AG2/AutoGen** (`ag2`) - Conversation-based multi-agent system

## 🚀 Quick Deployment Options

### Option 1: Coolify Deployment (Recommended)

The easiest way to deploy with automatic HTTPS, domain management, and monitoring:

```bash
# Use the Coolify-optimized configuration
# Simple version (FastAPI only)
cp docker-compose.coolify-simple.yml docker-compose.yml

# Full version (with monitoring)
cp docker-compose.coolify.yml docker-compose.yml
```

**See [COOLIFY_DEPLOYMENT_GUIDE.md](COOLIFY_DEPLOYMENT_GUIDE.md) for detailed instructions.**

### Option 2: Traditional Docker Compose

```bash
# Build and run with monitoring stack
docker-compose up -d

# Access the application
curl https://localhost/v1/health
```

## ⚙️ Environment Configuration

### Required Environment Variables

```bash
# Authentication (Clerk)
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Optional Configuration

```bash
# Performance
DEBUG=false
LOG_LEVEL=info
GUNICORN_WORKERS=4

# CORS
CORS_ORIGINS=["https://your-frontend.com"]
```

## 🔧 Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Supabase account
- Clerk account
- OpenAI/Anthropic API keys

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd fastapi-agent-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🧪 Testing

### Unit Tests
```bash
pytest tests/ -v
```

### Load Testing
```bash
# Install k6
# Run load tests targeting 20 RPS
k6 run tests/load-test.js
```

## 📊 Monitoring

### Prometheus Metrics
- HTTP request/response metrics
- Agent execution performance
- Token usage tracking
- System resource utilization

### Grafana Dashboards
- FastAPI performance dashboard
- AI agent execution metrics
- System health monitoring

Access Grafana at: `https://grafana.your-domain.com` (with full deployment)

## 🔒 Security Features

- **JWT Authentication**: Secure Clerk-based user authentication
- **Environment Variables**: All secrets stored securely outside code
- **HTTPS Enforcement**: Automatic SSL with Let's Encrypt (Coolify)
- **Security Headers**: Comprehensive security headers via reverse proxy
- **Input Validation**: Pydantic models for all API inputs
- **Rate Limiting**: Configurable rate limits (deployment-dependent)

## 📈 Performance

- **Target**: 20 RPS sustained load
- **P95 Latency**: <200ms for agent endpoints
- **Error Rate**: <5% threshold
- **Connection Pooling**: Optimized database connections
- **Async Operations**: Non-blocking I/O throughout

## 🔄 CI/CD

The repository is configured for:
- **Automatic deployments** via Coolify on git push
- **Health checks** for zero-downtime deployments
- **Rollback capability** on deployment failures
- **Load testing** integration for performance validation

## 📚 Documentation

- [Coolify Deployment Guide](COOLIFY_DEPLOYMENT_GUIDE.md) - Complete Coolify setup
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [Architecture Overview](.cursor/rules/project-overview.mdc) - Detailed system architecture
- [Agent System](.cursor/rules/agent-system.mdc) - AI agent implementation details
- [Supabase Connection Status](SUPABASE_CONNECTION_STATUS.md) - Guide for connecting to Supabase
- [Tauri Integration](TAURI_INTEGRATION.md) - Guide for connecting to Tauri desktop apps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Documentation**: See the `/docs` directory and `.cursor/rules/` files

---

## ⚙️ Admin Control Panel

The FastAPI Agent Backend includes a Streamlit-based admin control panel that allows you to configure the application through a user-friendly interface.

### Running the Admin Panel

1. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the admin panel** using one of these methods:

   **Option 1: Using the startup script (recommended)**:
   ```bash
   python admin/run_admin_panel.py
   ```

   **Option 2: Using Streamlit directly**:
   ```bash
   streamlit run admin/app.py
   ```

3. **Access the admin panel** in your web browser (typically at http://localhost:8501)

### Features of the Admin Panel

- Configure all application settings through a user-friendly UI
- Organized into logical sections for easy navigation
- Changes are saved directly to your `.env` file
- Secure handling of sensitive information like API keys and passwords

For more details, see the [Admin Panel Documentation](admin/README.md).

## 🎉 Quick Start Summary

1. **Clone this repository**
2. **Set up external services** (Supabase, Clerk, AI APIs)
3. **Choose deployment method**:
   - **Coolify**: Use `docker-compose.coolify-simple.yml` 
   - **Traditional**: Use `docker-compose.yml`
4. **Configure environment variables** (using the Admin Control Panel or manually)
5. **Set up integrations** (if needed):
   - **Tauri Desktop App**: Configure CORS and Tauri-specific settings
   - **Remote Supabase**: Configure enhanced connection options
6. **Deploy and enjoy your AI agent backend!**

Your FastAPI Agent Backend will be live with automatic HTTPS, monitoring, and enterprise-grade security! 🚀 
