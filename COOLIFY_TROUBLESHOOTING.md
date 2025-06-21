# 🔧 Coolify Deployment Troubleshooting Guide

## 🚨 **Container Starts But App Not Accessible**

Your deployment logs show the container starts successfully, but the app isn't responding. This is typically a configuration issue.

## 🔍 **Step-by-Step Debugging**

### **Step 1: Check Application Logs**

1. **In Coolify Dashboard:**
   - Go to your application
   - Click **"Logs"** tab
   - Look for these specific errors:

**Common Error Patterns:**
```bash
# Configuration errors
pydantic_settings.sources.SettingsError: error parsing value for field

# Missing environment variables
KeyError: 'CLERK_SECRET_KEY'
KeyError: 'SUPABASE_URL'

# Port binding issues
OSError: [Errno 98] Address already in use
uvicorn.error: Error binding to host

# Database connection errors
asyncpg.exceptions.InvalidCatalogNameError
supabase.exceptions.APIError
```

### **Step 2: Verify Environment Variables**

**Required Variables (Must be set):**
```bash
CLERK_SECRET_KEY=sk-test-...
CLERK_PUBLISHABLE_KEY=pk_test_...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql+asyncpg://postgres:password@db.project.supabase.co:5432/postgres
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Check in Coolify:**
1. Go to **Environment Variables** tab
2. Verify all required variables are present
3. Check for typos or extra spaces

### **Step 3: Test Container Health**

**In Coolify Dashboard:**
1. Go to **"Containers"** or **"Resources"** tab
2. Check container status:
   - ✅ **Running** = Good
   - ❌ **Exited/Failed** = Check logs
   - ⚠️ **Unhealthy** = Health check failing

### **Step 4: Check Port Configuration**

**Verify Port Settings:**
1. In Coolify, go to **"Network"** tab
2. Check **"Port Exposes"** field
3. Should be: `8000`
4. **NOT** `localhost:8000` or `127.0.0.1:8000`

### **Step 5: Test Internal Container**

**If you have SSH access to your server:**
```bash
# Find your container
docker ps | grep backend

# Test internal health check
docker exec <container-id> curl -f http://localhost:8000/v1/health

# Check if app is listening
docker exec <container-id> netstat -tlnp | grep 8000
```

## 🛠️ **Common Fixes**

### **Fix 1: Missing Environment Variables**

**Problem:** App crashes on startup due to missing config
**Solution:** Add all required environment variables in Coolify UI

### **Fix 2: Wrong Port Configuration**

**Problem:** App listens on localhost instead of 0.0.0.0
**Solution:** Already fixed in our code - app listens on `0.0.0.0:8000`

### **Fix 3: Health Check Failing**

**Problem:** Container marked as unhealthy
**Solution:** 
1. Go to Coolify **"Health Checks"** tab
2. Temporarily disable health check
3. Redeploy and test

### **Fix 4: Database Connection Issues**

**Problem:** Can't connect to Supabase
**Solution:**
1. Verify Supabase project is active
2. Check DATABASE_URL format:
   ```
   postgresql+asyncpg://postgres:PASSWORD@db.PROJECT-ID.supabase.co:5432/postgres
   ```
3. Test connection from Supabase dashboard

### **Fix 5: CORS Configuration**

**Problem:** Frontend can't connect
**Solution:** Already fixed - CORS set to `["*"]` for development

## 🎯 **Quick Diagnostic Commands**

**Test from your local machine:**
```bash
# Test health endpoint
curl -v https://k4cwok8ocggo4wkkswo048o0.atlas-agent.net/v1/health

# Test root endpoint
curl -v https://k4cwok8ocggo4wkkswo048o0.atlas-agent.net/

# Check if domain resolves
nslookup k4cwok8ocggo4wkkswo048o0.atlas-agent.net
```

## 🔄 **Recommended Actions**

### **Action 1: Switch to Optimized Config**
1. Change compose file to: `docker-compose.coolify-optimized.yml`
2. Redeploy

### **Action 2: Minimal Environment Test**
Set only these essential variables:
```bash
DEBUG=true
LOG_LEVEL=debug
CLERK_SECRET_KEY=dummy-key-for-testing
SUPABASE_URL=dummy-url-for-testing
OPENAI_API_KEY=dummy-key-for-testing
```

### **Action 3: Enable Debug Mode**
```bash
DEBUG=true
LOG_LEVEL=debug
```

## 📋 **Information to Collect**

When asking for help, provide:

1. **Application Logs** (from Coolify Logs tab)
2. **Container Status** (Running/Exited/Unhealthy)
3. **Environment Variables** (screenshot, hide sensitive values)
4. **Network Configuration** (Port Exposes setting)
5. **Error Messages** (exact text from logs)
6. **Curl Test Results** (from diagnostic commands above)

## 🆘 **Emergency Reset**

If nothing works:

1. **Delete the application** in Coolify
2. **Create new application** with:
   - Repository: `https://github.com/KB01111/fastapi-agent-backend.git`
   - Compose file: `docker-compose.coolify-optimized.yml`
   - Set minimal environment variables
3. **Deploy and test**

## 🎯 **Expected Working State**

When working correctly:
- ✅ Container status: **Running**
- ✅ Health check: **Healthy**
- ✅ `curl https://your-domain.com/v1/health` returns `{"status":"healthy"}`
- ✅ `curl https://your-domain.com/` returns API information
