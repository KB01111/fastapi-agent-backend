# 🚀 FastAPI AI Agent Backend - Complete Deployment Guide

## 📊 **Current Status: Ready for Production** ✅

Your AI agent backend is fully configured with all frameworks working. Here's how to deploy and connect it.

## 🏗️ **Deployment Options**

### **Option 1: VPS Deployment (Recommended)**

**Best for:** Production apps, custom domains, full control

#### **Requirements:**
- Ubuntu 22.04 VPS (2vCPU, 4GB RAM minimum)
- Domain name pointing to your server
- Basic server management knowledge

#### **Quick Setup:**
```bash
# 1. Server Preparation
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install docker-compose-plugin -y

# 2. Configure Firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw --force enable

# 3. Deploy Application
git clone <your-repo>
cd fastapi-agent-backend
cp env.example .env
# Edit .env with your API keys
nano .env

# 4. Update Domain
sed -i 's/your-domain.com/yourdomain.com/g' Caddyfile

# 5. Launch
docker-compose up -d
```

#### **VPS Providers:**
- **DigitalOcean**: $20/month (2vCPU, 4GB)
- **Linode**: $24/month (2vCPU, 4GB)
- **Vultr**: $20/month (2vCPU, 4GB)
- **Hetzner**: $15/month (2vCPU, 4GB)

---

### **Option 2: Railway Deployment**

**Best for:** Quick deployment, automatic scaling, no server management

#### **Setup Steps:**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up

# 3. Set environment variables
railway variables set OPENAI_API_KEY=sk-your-key
railway variables set ANTHROPIC_API_KEY=sk-ant-your-key
railway variables set CLERK_SECRET_KEY=sk_test_your-key
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_ANON_KEY=your-anon-key
railway variables set DATABASE_URL=postgresql+asyncpg://...
```

#### **Cost:** ~$5-20/month (pay-per-use)
#### **URL:** `https://your-app-name.railway.app`

---

### **Option 3: Render Deployment**

**Best for:** Free tier, automatic deployments, simple setup

#### **Setup:**
1. Connect GitHub repo to Render
2. Choose "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard

#### **Cost:** Free tier available, $7/month for production
#### **URL:** `https://your-app-name.onrender.com`

---

### **Option 4: Google Cloud Run**

**Best for:** Serverless, pay-per-request, automatic scaling

#### **Dockerfile Optimization:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### **Deploy:**
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-agent-backend
gcloud run deploy --image gcr.io/PROJECT-ID/ai-agent-backend --platform managed
```

#### **Cost:** Pay-per-request, ~$0-50/month depending on usage

---

## 🔗 **Frontend Connection Guide**

### **React/Next.js Integration**

```javascript
// lib/ai-agent-api.js
import { useAuth } from '@clerk/nextjs';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-domain.com';

export class AIAgentAPI {
  constructor(getToken) {
    this.getToken = getToken;
  }

  async callAgent(task, agentType = 'openai', context = {}) {
    const token = await this.getToken();
    
    const response = await fetch(`${API_BASE_URL}/v1/answer`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task,
        agent_type: agentType,
        context
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getAvailableAgents() {
    const token = await this.getToken();
    
    const response = await fetch(`${API_BASE_URL}/v1/agents`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    return response.json();
  }
}

// Usage in component
export function useAIAgent() {
  const { getToken } = useAuth();
  const api = new AIAgentAPI(getToken);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const executeTask = async (task, agentType) => {
    setLoading(true);
    try {
      const response = await api.callAgent(task, agentType);
      setResult(response);
      return response;
    } catch (error) {
      console.error('AI Agent Error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { executeTask, loading, result };
}
```

### **React Native/Expo Integration**

```javascript
// services/AIAgentService.js
import { useAuth } from '@clerk/expo';

export class AIAgentService {
  constructor(apiUrl = 'https://your-domain.com') {
    this.apiUrl = apiUrl;
  }

  async callAgent(getToken, task, agentType = 'openai') {
    try {
      const token = await getToken();
      
      const response = await fetch(`${this.apiUrl}/v1/answer`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task,
          agent_type: agentType,
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'API Error');
      }

      return data;
    } catch (error) {
      console.error('AI Agent Service Error:', error);
      throw error;
    }
  }
}

// Usage in component
import { AIAgentService } from '../services/AIAgentService';

export default function ChatScreen() {
  const { getToken } = useAuth();
  const aiService = new AIAgentService();
  
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    setLoading(true);
    try {
      const result = await aiService.callAgent(getToken, message, 'openai');
      setResponse(result.result);
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        value={message}
        onChangeText={setMessage}
        placeholder="Ask the AI agent..."
        style={styles.input}
      />
      <Button title="Send" onPress={handleSend} disabled={loading} />
      {response && <Text style={styles.response}>{response}</Text>}
    </View>
  );
}
```

### **Flutter Integration**

```dart
// lib/services/ai_agent_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class AIAgentService {
  final String baseUrl;
  
  AIAgentService({this.baseUrl = 'https://your-domain.com'});

  Future<Map<String, dynamic>> callAgent({
    required String token,
    required String task,
    String agentType = 'openai',
    Map<String, dynamic>? context,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/v1/answer'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'task': task,
        'agent_type': agentType,
        'context': context ?? {},
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to call AI agent: ${response.body}');
    }
  }
}
```

### **Python Client Integration**

```python
# ai_agent_client.py
import requests
import json

class AIAgentClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def call_agent(self, task: str, agent_type: str = 'openai', context: dict = None):
        """Call an AI agent with a task."""
        response = self.session.post(
            f'{self.base_url}/v1/answer',
            json={
                'task': task,
                'agent_type': agent_type,
                'context': context or {}
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_available_agents(self):
        """Get list of available agents."""
        response = self.session.get(f'{self.base_url}/v1/agents')
        response.raise_for_status()
        return response.json()

# Usage
client = AIAgentClient('https://your-domain.com', 'your-clerk-jwt')
result = client.call_agent('Analyze market trends', 'praisonai')
print(result['result'])
```

---

## ⚙️ **Environment Configuration**

### **Required Environment Variables**

```bash
# Authentication
CLERK_SECRET_KEY=sk_test_your-secret-key-here
CLERK_PUBLISHABLE_KEY=pk_test_your-publishable-key-here

# AI Providers
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql+asyncpg://postgres:password@db.your-project.supabase.co:5432/postgres

# Optional: Production Settings
DEBUG=false
LOG_LEVEL=info
WORKERS=4
```

### **Supabase Database Setup**

1. **Create Supabase Project**: Go to [supabase.com](https://supabase.com)
2. **Get Credentials**: Settings → API → Copy URL and anon key
3. **Database Setup**: The app will create tables automatically
4. **Enable RLS**: For security, enable Row Level Security on tables

---

## 🔒 **Security Configuration**

### **Production Security Checklist**

- ✅ **HTTPS/TLS**: Caddy provides automatic SSL certificates
- ✅ **JWT Validation**: Clerk handles authentication
- ✅ **CORS**: Configured for cross-origin requests
- ✅ **Rate Limiting**: Built into Caddy reverse proxy
- ✅ **Input Validation**: Pydantic models validate all inputs
- ✅ **SQL Injection Prevention**: SQLAlchemy with parameterized queries

### **Firewall Configuration (VPS)**

```bash
# Basic firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

---

## 📊 **Monitoring & Analytics**

### **Built-in Monitoring**

- **Grafana Dashboard**: `https://your-domain.com:3000`
  - Login: `admin/admin`
  - Pre-configured dashboards for API metrics
  
- **Prometheus Metrics**: `https://your-domain.com:9090`
  - Raw metrics and targets
  
- **Health Check**: `https://your-domain.com/v1/health`
  - API status and agent availability

### **Key Metrics to Monitor**

```python
# Available metrics
- HTTP request duration (P95 < 200ms target)
- Error rates (< 5% target)
- Agent execution times
- Token usage per agent type
- Database connection pool status
- Memory and CPU usage
```

---

## 🧪 **Testing Your Deployment**

### **API Testing Script**

```bash
#!/bin/bash
API_URL="https://your-domain.com"
JWT_TOKEN="your-clerk-jwt-token"

echo "🧪 Testing AI Agent Backend"
echo "================================"

# Test health endpoint
echo "Testing health endpoint..."
curl -s "$API_URL/v1/health" | jq '.'

# Test agents list
echo "Testing agents endpoint..."
curl -s -H "Authorization: Bearer $JWT_TOKEN" "$API_URL/v1/agents" | jq '.'

# Test agent execution
echo "Testing OpenAI agent..."
curl -s -X POST "$API_URL/v1/answer" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Hello, how are you?",
    "agent_type": "openai"
  }' | jq '.'

echo "✅ Testing complete!"
```

### **Load Testing**

```bash
# Install k6 for load testing
sudo apt install k6

# Run load test
k6 run --vus 10 --duration 30s tests/load-test.js
```

---

## 💰 **Cost Estimation**

### **Monthly Hosting Costs**

| Platform | Configuration | Cost/Month | Best For |
|----------|---------------|------------|----------|
| **VPS (DigitalOcean)** | 2vCPU, 4GB RAM | $20 | Production, Custom Domain |
| **Railway** | 2GB RAM, Pay-per-use | $5-20 | Auto-scaling, Simple Deploy |
| **Render** | 0.5GB RAM | Free-$7 | Development, Small Apps |
| **Google Cloud Run** | Pay-per-request | $0-50 | Serverless, Variable Load |

### **API Usage Costs**

- **OpenAI API**: ~$0.002 per 1K tokens
- **Anthropic API**: ~$0.003 per 1K tokens
- **Clerk Auth**: Free tier: 10K MAU, then $0.02/user
- **Supabase**: Free tier: 500MB DB, then $25/month

---

## 🚀 **Quick Start Commands**

### **VPS Deployment (Copy & Paste)**

```bash
# One-line deployment script
curl -sSL https://raw.githubusercontent.com/your-repo/fastapi-agent-backend/main/deploy.sh | bash
```

### **Local Development**

```bash
# Start development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test in browser
open http://localhost:8000/docs
```

### **Docker Deployment**

```bash
# Build and run locally
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
```

---

## 📞 **Support & Troubleshooting**

### **Common Issues**

1. **502 Bad Gateway**: Check if backend container is running
2. **Authentication Failed**: Verify Clerk JWT token format
3. **AI Agent Timeout**: Increase timeout in agent execution
4. **Database Connection**: Check Supabase URL and credentials

### **Debug Commands**

```bash
# Check container status
docker-compose ps

# View application logs
docker-compose logs -f backend

# Test database connection
docker-compose exec backend python -c "from app.database import engine; print('DB OK')"

# Test AI agents
docker-compose exec backend python -c "from app.agents import orchestrator; print(orchestrator.get_available_agents())"
```

---

## 🎉 **You're Ready!**

Your FastAPI AI Agent Backend is now ready for production deployment with:

✅ **6 AI Frameworks** (PraisonAI, CrewAI, AutoGen, OpenAI, Anthropic, Mock)  
✅ **Multiple Deployment Options** (VPS, Railway, Render, Cloud Run)  
✅ **Frontend Integration Examples** (React, React Native, Flutter, Python)  
✅ **Production Security** (HTTPS, JWT, Rate Limiting)  
✅ **Monitoring & Analytics** (Grafana, Prometheus)  
✅ **Comprehensive Testing** (Health checks, Load testing)  

Choose your deployment option and start building amazing AI-powered applications! 🚀 