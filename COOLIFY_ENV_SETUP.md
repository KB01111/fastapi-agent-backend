# 🔧 Coolify Environment Variables Setup

## 🚨 **CORS Configuration Fix**

The deployment error was caused by malformed CORS_ORIGINS. This is now fixed in the Docker Compose files.

## ✅ **Required Environment Variables**

Copy these **exact values** into your Coolify environment variables:

### **Authentication (Required)**
```bash
CLERK_SECRET_KEY=your_actual_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=your_actual_clerk_publishable_key_here
JWT_ALGORITHM=RS256
```

### **Database (Required)**
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.your-project-id.supabase.co:5432/postgres
SUPABASE_DIRECT_URL=postgresql://postgres:your_password@db.your-project-id.supabase.co:5432/postgres
SUPABASE_CONNECTION_POOLING=true
```

### **AI Services (Required)**
```bash
OPENAI_API_KEY=sk-your_openai_api_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

### **Application Configuration (Optional)**
```bash
DEBUG=false
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000
GUNICORN_WORKERS=2
```

### **AI Framework Control (Fast Build)**
```bash
AI_FRAMEWORKS_ENABLED=false
PRAISONAI_ENABLED=false
CREWAI_ENABLED=false
AUTOGEN_ENABLED=false
```

## 🎯 **CORS Configuration (Fixed)**

The CORS configuration is now hardcoded in the Docker Compose files as:
```yaml
- CORS_ORIGINS=["*"]
```

This allows all origins for development. For production, you can customize this by setting:
```bash
CORS_ORIGINS=["https://your-frontend-domain.com","https://your-app.com"]
```

## 🚀 **Deployment Steps**

1. **In Coolify Dashboard:**
   - Go to your application
   - Click "Environment Variables"
   - Add each variable from the "Required" sections above
   - **Important:** Use `docker-compose.coolify-fast.yml` as compose file

2. **Deploy:**
   - Click "Deploy"
   - Build should complete in 2-5 minutes
   - Application should start successfully

## 🔍 **Troubleshooting**

### **If you get CORS errors:**
- The CORS configuration is now fixed to allow all origins
- For production, customize the CORS_ORIGINS variable

### **If you get authentication errors:**
- Verify your Clerk keys are correct
- Check that JWT_ALGORITHM is set to "RS256"

### **If you get database errors:**
- Verify your Supabase connection details
- Test the DATABASE_URL format
- Ensure your Supabase project is active

### **If you get AI service errors:**
- Verify your OpenAI API key starts with "sk-"
- Check your Anthropic API key starts with "sk-ant-"
- Ensure you have sufficient credits

## ✅ **Success Indicators**

Your deployment is successful when:
- ✅ Build completes in 2-5 minutes
- ✅ Container starts without errors
- ✅ Health check at `/v1/health` returns 200
- ✅ Root endpoint `/` returns API information

## 🎉 **Next Steps**

Once deployed successfully:
1. Test the health endpoint: `https://your-domain.com/v1/health`
2. Test the API info: `https://your-domain.com/`
3. Configure your frontend to use the new backend URL
4. Test authentication with your Clerk setup
