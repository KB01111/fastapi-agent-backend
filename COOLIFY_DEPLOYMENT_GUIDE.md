# Coolify Deployment Guide for FastAPI Agent Backend

This guide provides step-by-step instructions for deploying your FastAPI Agent Backend on Coolify, including both simple and full monitoring setups.

## 🎯 **Quick Start (Recommended)**

For most deployments, use the simplified configuration:

### 1. **Prepare Your Repository**

```bash
# Ensure you have the correct files in your repository
git add docker-compose.coolify-simple.yml
git add Dockerfile
git add app/
git add requirements.txt
git commit -m "Add Coolify deployment configuration"
git push
```

### 2. **Deploy in Coolify**

1. **Create New Application**:
   - Go to your Coolify dashboard
   - Click "Create New" → "Docker Compose"
   - Select your repository
   - Set compose file path: `docker-compose.coolify-simple.yml`

2. **Configure Environment Variables**:
   Coolify will automatically detect these variables from your compose file:

   ```bash
   # Authentication (Required)
   CLERK_SECRET_KEY=your_clerk_secret_key
   CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key

   # Database (Required)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

   # Enhanced Supabase Connection (Recommended for production)
   SUPABASE_DIRECT_URL=postgresql://user:pass@host:5432/dbname
   SUPABASE_CONNECTION_POOLING=true

   # AI Services (Required)
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key

   # Optional Configuration
   DEBUG=false
   LOG_LEVEL=info
   GUNICORN_WORKERS=2

   # Tauri Desktop App Integration (Optional)
   TAURI_ENABLED=false
   TAURI_ALLOWED_ORIGINS=["tauri://localhost","tauri://*"]
   ```

3. **Deploy**:
   - Click "Deploy"
   - Coolify will automatically:
     - Generate a unique FQDN (e.g., `backend-abc123.your-domain.com`)
     - Set up automatic HTTPS with Let's Encrypt
     - Configure Traefik routing
     - Create necessary directories

## 🚀 **Advanced Deployment (With Monitoring)**

For production deployments with full monitoring stack:

### Use Full Configuration

```bash
# Use the full monitoring configuration
cp docker-compose.coolify.yml docker-compose.yml
```

This includes:
- **Prometheus** for metrics collection
- **Grafana** for visualization dashboards
- **Advanced routing** for metrics endpoints
- **Security middleware** configuration

## 🔧 **Coolify-Specific Features Used**

### **Magic Environment Variables**

Your configuration uses Coolify's automatic domain generation:

```yaml
environment:
  - SERVICE_FQDN_BACKEND  # Auto-generates: https://backend-xyz.domain.com
  - SERVICE_PASSWORD_GRAFANA_ADMIN  # Auto-generates secure passwords
```

### **Automatic Directory Creation**

```yaml
volumes:
  - type: bind
    source: ./logs
    target: /app/logs
    is_directory: true  # Coolify creates this directory automatically
```

### **File Generation with Content**

```yaml
volumes:
  - type: bind
    source: ./prometheus.yml
    target: /etc/prometheus/prometheus.yml
    content: |  # Coolify creates file with this content
      global:
        scrape_interval: 15s
```

### **Traefik Integration**

Automatic routing and HTTPS:

```yaml
labels:
  - traefik.enable=true
  - "traefik.http.routers.backend.rule=Host(`$SERVICE_FQDN_BACKEND`)"
  - traefik.http.routers.backend.entrypoints=websecure
  - traefik.http.routers.backend.tls.certresolver=letsencrypt
```

## 🔌 **Enhanced Supabase Connection Options**

For better performance and reliability with Supabase, especially in production environments:

1. **Direct Connection URL**:
   ```bash
   # Bypasses the Supabase API for direct PostgreSQL access
   SUPABASE_DIRECT_URL=postgresql://postgres:password@your-project.supabase.co:5432/postgres
   ```

2. **Connection Pooling**:
   ```bash
   # Improves performance by reusing database connections
   SUPABASE_CONNECTION_POOLING=true
   ```

3. **Benefits**:
   - Reduced latency for database operations
   - Better handling of concurrent requests
   - More stable connections for production workloads
   - Improved performance under high load

## 🖥️ **Tauri Desktop App Integration**

If you're building a desktop application with Tauri that needs to connect to your FastAPI backend:

1. **Enable Tauri Integration**:
   ```bash
   # In your .env file or Coolify environment variables
   TAURI_ENABLED=true
   TAURI_ALLOWED_ORIGINS=["tauri://localhost","tauri://*"]
   ```

2. **Configure CORS for Tauri**:
   ```bash
   # Make sure Tauri origins are included in CORS_ORIGINS
   CORS_ORIGINS=["https://your-domain.com","tauri://localhost","tauri://*"]
   ```

3. **In Your Tauri Application**:
   - Configure your Tauri app to connect to your Coolify-deployed backend
   - Use the generated Coolify FQDN in your Tauri app configuration
   - See [TAURI_INTEGRATION.md](TAURI_INTEGRATION.md) for detailed instructions

## 📋 **Pre-Deployment Checklist**

### **External Services Setup**

✅ **Supabase Database**:
- Create Supabase project
- Note the connection details
- Ensure database tables are created (will auto-create on first run)

✅ **Clerk Authentication**:
- Create Clerk application
- Get publishable and secret keys
- Configure allowed origins with your Coolify domain

✅ **AI Services**:
- OpenAI API key with sufficient credits
- Anthropic API key (optional but recommended)

### **Repository Preparation**

✅ **Required Files**:
- `Dockerfile` (multi-stage build)
- `docker-compose.coolify-simple.yml` or `docker-compose.coolify.yml`
- `requirements.txt`
- `app/` directory with your FastAPI application

✅ **Optional Files**:
- `gunicorn.conf.py` (for production WSGI config)
- `.dockerignore` (optimize build performance)

## 🎮 **Deployment Options**

### **Option 1: Simple Backend Only**
```bash
# File: docker-compose.coolify-simple.yml
# Contains: FastAPI backend only
# Best for: Development, simple production setups
```

### **Option 2: Full Monitoring Stack**
```bash
# File: docker-compose.coolify.yml  
# Contains: FastAPI + Prometheus + Grafana
# Best for: Production with observability requirements
```

### **Option 3: Custom Configuration**
Modify either file to:
- Add Redis for caching
- Include additional worker services
- Add custom middleware

## 🔒 **Security Considerations**

### **Automatic HTTPS**
Coolify automatically provides:
- Let's Encrypt SSL certificates
- HTTP to HTTPS redirects
- Security headers via Traefik

### **Environment Variables**
- All sensitive data stored securely in Coolify
- No secrets in Docker images or repository
- Environment variables encrypted at rest

### **Network Security**
- Services communicate via internal Docker networks
- Only necessary ports exposed via Traefik
- Metrics endpoints can be IP-restricted

## 📊 **Monitoring Setup (Full Configuration)**

### **Prometheus Metrics**
Available at: `https://your-domain.com/metrics` (IP-restricted)

Metrics include:
- HTTP request/response times
- Agent execution performance
- Token usage tracking
- System resource utilization

### **Grafana Dashboards**
Available at: `https://grafana-xyz.your-domain.com`

Auto-configured with:
- Prometheus data source
- FastAPI performance dashboard
- Agent execution metrics
- System health monitoring

## 🛠️ **Troubleshooting**

### **Common Issues**

**Build Failures**:
```bash
# Check Dockerfile syntax
docker build . --target production

# Verify requirements.txt
pip install -r requirements.txt
```

**Environment Variable Issues**:
- Ensure all required variables are set in Coolify UI
- Check variable names match exactly (case-sensitive)
- Verify no extra spaces in values

**Domain/FQDN Issues**:
- Wait 2-3 minutes after deployment for DNS propagation
- Check Coolify logs for Traefik routing issues
- Verify domain configuration in Coolify settings

**Health Check Failures**:
```yaml
# Verify health endpoint responds
curl -f http://localhost:8000/v1/health

# Check application logs in Coolify
# Adjust health check timing if needed
```

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
```yaml
environment:
  - GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}  # Increase for more traffic
```

### **Resource Limits**
Configure in Coolify UI:
- CPU limits
- Memory limits  
- Disk space allocation

### **Database Scaling**
- Supabase automatically handles scaling
- Consider connection pooling for high traffic
- Monitor database performance metrics

## 🔄 **Deployment Pipeline**

### **Automatic Deployments**
Coolify can automatically deploy on:
- Git push to main branch
- Manual trigger via UI
- Webhook integration
- Scheduled deployments

### **Blue-Green Deployments**
- Coolify supports zero-downtime deployments
- Old version kept running until new version is healthy
- Automatic rollback on health check failures

## 📚 **Additional Resources**

- [Coolify Documentation](https://coolify.io/docs)
- [Traefik Routing Guide](https://doc.traefik.io/traefik/routing/routers/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

---

## 🎉 **Quick Deploy Command**

For the fastest deployment:

1. Copy `docker-compose.coolify-simple.yml` to your repository
2. Create new Docker Compose application in Coolify
3. Set environment variables in Coolify UI
4. Deploy!

Your FastAPI Agent Backend will be live with automatic HTTPS and domain management! 
