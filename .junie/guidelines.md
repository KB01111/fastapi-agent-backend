# Project Guidelines for FastAPI Agent Backend

## Project Overview
This is a FastAPI Agent Backend project that orchestrates multiple AI agents with secure authentication, database persistence, and comprehensive monitoring. The project provides a unified interface for working with different AI agent frameworks including PraisonAI, CrewAI, and AG2/AutoGen.

## Project Structure
- **app/main.py**: Main entry point with middleware configuration and route setup
- **app/agents.py**: Core AI agent orchestration system with implementations for multiple frameworks
- **app/api/v1/**: API endpoints for agent interaction
- **app/auth.py**: Authentication layer with Clerk JWT verification
- **app/database.py**: Database layer with Supabase PostgreSQL and SQLAlchemy ORM
- **app/monitoring.py**: Prometheus metrics and structured logging
- **app/integrations/**: External service integrations (MindsDB, Gmail)
- **app/config.py**: Application configuration and settings
- **tests/**: Unit tests and load tests

## Testing Instructions
1. **Unit Tests**:
   ```bash
   pytest tests/ -v
   ```

2. **Load Testing**:
   ```bash
   # Install k6 first
   k6 run tests/load-test.js
   ```

3. **Test Coverage**:
   Junie should run tests to check the correctness of proposed solutions, especially when modifying core components like the agent orchestration system or API endpoints.

## Build and Deployment Instructions
1. **Local Development**:
   ```bash
   # Create virtual environment
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # Install dependencies
   pip install -r requirements.txt
   # Run the application
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Docker Deployment**:
   ```bash
   # Build and run with monitoring stack
   docker-compose up -d
   ```

3. **Coolify Deployment** (Recommended):
   ```bash
   # Simple version (FastAPI only)
   cp docker-compose.coolify-simple.yml docker-compose.yml
   # Full version (with monitoring)
   cp docker-compose.coolify.yml docker-compose.yml
   ```

4. **Environment Configuration**:
   - Copy `env.example` to `.env` and configure required variables
   - Ensure all required external services are properly set up (Supabase, Clerk, etc.)

## Code Style Guidelines
1. **Python Style**:
   - Follow PEP 8 guidelines for Python code
   - Use type hints for function parameters and return values
   - Document classes and functions with docstrings

2. **API Design**:
   - Use Pydantic models for request/response validation
   - Follow RESTful principles for API endpoints
   - Implement proper error handling and status codes

3. **Testing**:
   - Write unit tests for new functionality
   - Ensure tests cover edge cases and error scenarios
   - Maintain or improve test coverage when modifying existing code

4. **Documentation**:
   - Update documentation when adding new features or changing existing ones
   - Include examples for API usage
   - Document environment variables and configuration options

5. **Performance Considerations**:
   - Use async/await for I/O-bound operations
   - Implement proper connection pooling for database operations
   - Monitor and optimize token usage for AI operations

## Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Monitoring and Observability
- Prometheus metrics are available at the `/metrics` endpoint
- Grafana dashboards are included for visualizing metrics
- Structured logging is implemented throughout the application
