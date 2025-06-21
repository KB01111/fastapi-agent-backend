# 🎯 **Connect FastAPI Backend to Supabase Cloud**

## ✅ **Your Supabase Project Details**

- **Project Name**: KB01111's Project
- **Project ID**: `dgqhxtrvoebwhjsllcck`
- **Region**: eu-central-1
- **Status**: ACTIVE_HEALTHY
- **Database Host**: `db.dgqhxtrvoebwhjsllcck.supabase.co`

## 🔑 **Step 1: Get Your Database Password**

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Select**: "KB01111's Project"
3. **Go to**: Settings → Database
4. **Copy your database password** (set when you created the project)

## 🔧 **Step 2: Configure Environment Variables in Coolify**

**In your Coolify Dashboard, add these environment variables:**

```bash
# Supabase Configuration - EXACT VALUES
SUPABASE_URL=https://dgqhxtrvoebwhjsllcck.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRncWh4dHJ2b2Vid2hqc2xsY2NrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDExMTcxNDMsImV4cCI6MjA1NjY5MzE0M30.m6fpdSs36vpI6A_cRyHLGKr9qN0DsSP9jeulV5FPkaQ
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRncWh4dHJ2b2Vid2hqc2xsY2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MTExNzE0MywiZXhwIjoyMDU2NjkzMTQzfQ.nRXLFYMPTID5vDr68qSVjSaMfynFjN-8fVBijNc-aK4

# Database Connection - REPLACE YOUR_DB_PASSWORD
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_DB_PASSWORD@db.dgqhxtrvoebwhjsllcck.supabase.co:5432/postgres
SUPABASE_DIRECT_URL=postgresql://postgres:YOUR_DB_PASSWORD@db.dgqhxtrvoebwhjsllcck.supabase.co:5432/postgres
SUPABASE_CONNECTION_POOLING=true

# Other Required Variables (if not set)
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## 🚀 **Step 3: Deploy with Supabase Connection**

1. **In Coolify Dashboard:**
   - Add all environment variables above
   - **Replace `YOUR_DB_PASSWORD`** with your actual Supabase password
   - Click "Deploy"

2. **Monitor deployment logs** for these success messages:
   ```
   INFO: Database engine initialized successfully
   INFO: Supabase client initialized successfully
   INFO: Database tables initialized successfully
   ```

## 🧪 **Step 4: Test Database Connection**

After deployment, test these endpoints:

### **Health Check (Should work now):**
```bash
https://k4cwok8ocggo4wkkswo048o0.atlas-agent.net/v1/health
```
**Expected:** `{"status":"healthy","service":"fastapi-agent-backend","version":"1.0.0"}`

### **Create a Test Session:**
```bash
curl -X POST "https://k4cwok8ocggo4wkkswo048o0.atlas-agent.net/v1/sessions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_CLERK_JWT" \
  -d '{"session_name": "Test Connection"}'
```

## 📊 **Database Tables (Auto-Created)**

Your FastAPI app will automatically create these tables in Supabase:

### **1. `agent_sessions`**
Stores conversation sessions:
- `id` (varchar) - Session UUID
- `user_id` (varchar) - Clerk user ID
- `session_name` (varchar) - Optional name
- `created_at` (timestamp) - Creation time
- `updated_at` (timestamp) - Last update
- `is_active` (boolean) - Active status
- `meta_data` (json) - Additional data

### **2. `agent_messages`**
Stores individual messages:
- `id` (varchar) - Message UUID
- `session_id` (varchar) - Related session
- `user_id` (varchar) - User ID
- `message_type` (varchar) - 'user', 'assistant', 'system'
- `content` (text) - Message content
- `created_at` (timestamp) - Message time
- `meta_data` (json) - Message metadata
- `token_count` (integer) - Token usage

### **3. `agent_executions`**
Stores execution logs:
- `id` (varchar) - Execution UUID
- `session_id` (varchar) - Related session
- `user_id` (varchar) - User ID
- `agent_type` (varchar) - Agent used
- `task` (text) - Task description
- `status` (varchar) - Execution status
- `result` (text) - Execution result
- `error_message` (text) - Error details
- `execution_time_ms` (integer) - Performance
- `token_usage` (json) - Token consumption
- `created_at` (timestamp) - Start time
- `completed_at` (timestamp) - End time
- `meta_data` (json) - Additional data

## 🔍 **Verify in Supabase Dashboard**

1. **Go to**: https://supabase.com/dashboard
2. **Select**: "KB01111's Project"
3. **Go to**: Table Editor
4. **Check**: You should see the 3 tables created automatically

## 🎯 **Connection Status Indicators**

### **✅ Success Indicators:**
- Health endpoint returns 200 OK
- Application logs show "Database initialized successfully"
- Tables appear in Supabase dashboard
- No database connection errors in logs

### **❌ Failure Indicators:**
- "no available server" error continues
- Database connection errors in logs
- Tables not created in Supabase
- Health endpoint still fails

## 🆘 **Troubleshooting**

### **If connection fails:**

1. **Check password format** - no special characters that need escaping
2. **Verify project is active** in Supabase dashboard
3. **Check firewall settings** - Supabase should allow all connections
4. **Test connection string** format is correct

### **Common Issues:**

**Issue**: Password contains special characters
**Solution**: URL-encode the password or use a simpler password

**Issue**: Connection timeout
**Solution**: Check if Supabase project is paused (free tier)

**Issue**: Authentication failed
**Solution**: Verify password is correct in Supabase settings

## 🎉 **Next Steps After Connection**

Once Supabase is connected:

1. **Test AI agent endpoints** with authentication
2. **Monitor database usage** in Supabase dashboard
3. **Set up Row Level Security** for production
4. **Configure backups** and monitoring

Your FastAPI Agent Backend will now have full database persistence! 🚀
