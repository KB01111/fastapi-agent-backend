# 🔗 Supabase Connection Setup Guide

This guide will help you connect your FastAPI Agent Backend to your Supabase database.

## 📋 Prerequisites

1. **Supabase Project**: Create a project at [supabase.com](https://supabase.com)
2. **Python Environment**: Make sure all dependencies are installed
3. **Environment Variables**: `.env` file configured with your credentials

## 🚀 Step-by-Step Setup

### Step 1: Get Your Supabase Credentials

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings → API**
4. Copy the following values:

```bash
# Project URL
https://your-project-id.supabase.co

# Anon (public) key 
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Service role (secret) key
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

5. Go to **Settings → Database**
6. Copy the **Connection string** and convert to async format:

```bash
# Original format:
postgresql://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres

# Convert to async format:
postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres
```

### Step 2: Configure Environment Variables

Open your `.env` file and update these values:

```bash
# Database (Supabase) - REQUIRED
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql+asyncpg://postgres:your-password@db.your-project-id.supabase.co:5432/postgres

# Authentication (Clerk) - Get from Clerk Dashboard
CLERK_SECRET_KEY=sk_test_your_actual_clerk_secret_key
CLERK_PUBLISHABLE_KEY=pk_test_your_actual_clerk_publishable_key

# AI Configuration - Get from OpenAI/Anthropic
OPENAI_API_KEY=sk-your-actual-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key
```

### Step 3: Test Database Connection

Run this command to test your connection:

```bash
python -c "
import asyncio
from app.database import engine
from sqlalchemy import text

async def test_connection():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT version()'))
            version = result.fetchone()[0]
            print('✅ Database connected successfully!')
            print(f'PostgreSQL version: {version[:50]}...')
    except Exception as e:
        print(f'❌ Connection failed: {e}')

asyncio.run(test_connection())
"
```

### Step 4: Create Database Tables

Run this command to create the necessary tables:

```bash
python -c "
import asyncio
from app.database import init_database

async def setup_tables():
    try:
        await init_database()
        print('✅ Database tables created successfully!')
    except Exception as e:
        print(f'❌ Table creation failed: {e}')

asyncio.run(setup_tables())
"
```

### Step 5: Verify Setup

Test the complete setup by running a quick verification:

```bash
python -c "
import asyncio
from app.database import db_manager

async def verify_setup():
    try:
        # Test creating a session
        session_id = await db_manager.create_session(
            user_id='test_user',
            session_name='Verification Test'
        )
        print(f'✅ Created test session: {session_id}')
        
        # Test saving a message
        message_id = await db_manager.save_message(
            session_id=session_id,
            user_id='test_user',
            message_type='user',
            content='Test message',
            metadata={'test': True}
        )
        print(f'✅ Saved test message: {message_id}')
        
        print('🎉 Supabase connection fully working!')
        
    except Exception as e:
        print(f'❌ Verification failed: {e}')

asyncio.run(verify_setup())
"
```

## 📊 Database Schema

Your FastAPI backend will create these tables in Supabase:

### `agent_sessions`
Stores conversation sessions between users and agents.

| Column | Type | Description |
|--------|------|-------------|
| `id` | varchar(255) | Primary key (UUID) |
| `user_id` | varchar(255) | User identifier from Clerk |
| `session_name` | varchar(255) | Optional session name |
| `created_at` | timestamp | Session creation time |
| `updated_at` | timestamp | Last update time |
| `is_active` | boolean | Whether session is active |
| `meta_data` | json | Additional metadata |

### `agent_messages`
Stores individual messages within sessions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | varchar(255) | Primary key (UUID) |
| `session_id` | varchar(255) | Foreign key to sessions |
| `user_id` | varchar(255) | User identifier |
| `message_type` | varchar(50) | 'user', 'assistant', 'system' |
| `content` | text | Message content |
| `created_at` | timestamp | Message timestamp |
| `meta_data` | json | Additional metadata |
| `token_count` | integer | Token usage count |

### `agent_executions`
Stores agent execution logs and metrics.

| Column | Type | Description |
|--------|------|-------------|
| `id` | varchar(255) | Primary key (UUID) |
| `session_id` | varchar(255) | Foreign key to sessions |
| `user_id` | varchar(255) | User identifier |
| `agent_type` | varchar(50) | Agent type used |
| `task` | text | Task description |
| `status` | varchar(50) | Execution status |
| `result` | text | Execution result |
| `error_message` | text | Error message if failed |
| `execution_time_ms` | integer | Execution time |
| `token_usage` | json | Token usage statistics |
| `created_at` | timestamp | Execution start time |
| `completed_at` | timestamp | Execution completion time |
| `meta_data` | json | Additional metadata |

## 🔍 Troubleshooting

### Common Issues

**1. Connection Refused**
```
❌ Connection failed: connection refused
```
- Check your `DATABASE_URL` format
- Ensure you're using `postgresql+asyncpg://` prefix
- Verify your Supabase project is active

**2. Authentication Failed**
```
❌ Connection failed: password authentication failed
```
- Double-check your database password
- Make sure you're using the correct user (usually `postgres`)
- Verify the connection string from Supabase dashboard

**3. Invalid API Key**
```
❌ Failed to initialize Supabase client: Invalid API key
```
- Check your `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Make sure there are no extra spaces or quotes
- Verify keys are from the correct project

**4. Table Already Exists**
```
❌ Table creation failed: relation "agent_sessions" already exists
```
- This is normal if tables were created before
- The error can be safely ignored

### Database Access in Supabase Dashboard

1. Go to **Table Editor** in your Supabase dashboard
2. You should see the new tables: `agent_sessions`, `agent_messages`, `agent_executions`
3. You can view and query data directly in the dashboard

### SQL Queries for Verification

Run these in the Supabase SQL Editor to verify your setup:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('agent_sessions', 'agent_messages', 'agent_executions');

-- View table structures
\d agent_sessions;
\d agent_messages;
\d agent_executions;

-- Check for test data
SELECT COUNT(*) as session_count FROM agent_sessions;
SELECT COUNT(*) as message_count FROM agent_messages;
SELECT COUNT(*) as execution_count FROM agent_executions;
```

## 🚀 Next Steps

Once Supabase is connected:

1. **Install AI Dependencies**:
   ```bash
   pip install praisonaiagents crewai pyautogen anthropic
   ```

2. **Start Development Server**:
   ```bash
   python app/main.py
   ```

3. **Test API Endpoints**:
   ```bash
   curl http://localhost:8000/v1/health
   curl http://localhost:8000/v1/agents
   ```

4. **Deploy with Docker**:
   ```bash
   docker-compose up -d
   ```

## 📚 API Usage Example

Once connected to Supabase, your API will automatically persist all conversations:

```bash
# Create a session
curl -X POST "http://localhost:8000/v1/sessions" \
  -H "Authorization: Bearer your-clerk-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"session_name": "My AI Chat"}'

# Send a message (automatically saved to Supabase)
curl -X POST "http://localhost:8000/v1/answer" \
  -H "Authorization: Bearer your-clerk-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Explain quantum computing",
    "agent_type": "openai",
    "session_id": "session-uuid-from-above"
  }'
```

All messages, sessions, and executions will be automatically stored in your Supabase database! 🎉 