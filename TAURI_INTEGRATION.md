# Connecting to Tauri Desktop Application

This guide explains how to configure your FastAPI Agent Backend to connect to a Tauri desktop application.

## Overview

[Tauri](https://tauri.app/) is a framework for building tiny, blazingly fast binaries for all major desktop platforms. It allows you to build desktop applications using web technologies (HTML, CSS, JavaScript) with a Rust backend. The FastAPI Agent Backend can be integrated with Tauri applications to provide AI agent capabilities to desktop applications.

## Configuration Options

The FastAPI Agent Backend supports the following Tauri-specific configuration options:

1. **TAURI_ENABLED**: Enable or disable Tauri integration (default: false)
2. **TAURI_ALLOWED_ORIGINS**: List of allowed Tauri origins (default: ["tauri://localhost", "tauri://*"])
3. **CORS_ORIGINS**: List of allowed CORS origins, which should include Tauri origins

## Setting Up Tauri Integration

### Step 1: Configure Your FastAPI Agent Backend

You can configure your FastAPI Agent Backend to connect to your Tauri application using one of the following methods:

#### Option 1: Using the Admin Panel (Recommended)

1. Run the admin panel: `python admin/run_admin_panel.py`
2. Navigate to the "Tauri Configuration" section
3. Enable Tauri integration
4. Configure the allowed Tauri origins
5. Navigate to the "CORS Configuration" section
6. Make sure Tauri origins are included in the CORS origins (you can use the "Quick Add for Tauri" button)

#### Option 2: Editing the .env File Directly

Add the following to your `.env` file:

```
# Tauri Configuration
TAURI_ENABLED=true
TAURI_ALLOWED_ORIGINS=["tauri://localhost","tauri://*"]

# CORS Configuration (include Tauri origins)
CORS_ORIGINS=["https://your-domain.com","http://localhost:3000","tauri://localhost","tauri://*"]
```

### Step 2: Configure Your Tauri Application

In your Tauri application, you need to configure it to communicate with your FastAPI Agent Backend:

1. **Update Tauri Configuration**: In your `tauri.conf.json` file, add the FastAPI backend URL to the allowed domains:

```json
{
  "tauri": {
    "allowlist": {
      "http": {
        "all": false,
        "request": true,
        "scope": ["http://localhost:8000/*", "https://your-api-domain.com/*"]
      }
    }
  }
}
```

2. **Make API Requests**: In your Tauri application code, you can make requests to your FastAPI backend:

```javascript
import { invoke } from '@tauri-apps/api/tauri';
import { fetch } from '@tauri-apps/api/http';

// Example function to call the FastAPI backend
async function callAgent(task) {
  try {
    const response = await fetch('http://localhost:8000/v1/answer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${yourAuthToken}`
      },
      body: JSON.stringify({
        task: task,
        agent_type: 'openai'
      })
    });
    
    return response.data;
  } catch (error) {
    console.error('Error calling agent:', error);
    throw error;
  }
}
```

## Security Considerations

When connecting your FastAPI Agent Backend to a Tauri application, consider the following security best practices:

1. **Use HTTPS**: In production, always use HTTPS for communication between your Tauri app and FastAPI backend
2. **Implement Proper Authentication**: Use Clerk or another authentication provider to secure your API
3. **Limit CORS Origins**: Only allow specific Tauri origins in your CORS configuration
4. **Validate Input**: Always validate input from the Tauri application on the server side

## Troubleshooting

### CORS Issues

If you're experiencing CORS issues when connecting your Tauri application to the FastAPI backend, check the following:

1. Make sure `TAURI_ENABLED` is set to `true` in your `.env` file
2. Verify that your Tauri origins are included in the `CORS_ORIGINS` list
3. Check the browser console for specific CORS error messages
4. Ensure your Tauri application is making requests with the correct headers

### Authentication Issues

If you're having trouble with authentication:

1. Make sure your Tauri application is sending the correct authentication headers
2. Verify that your Clerk configuration is correct
3. Check the FastAPI backend logs for authentication-related errors

## Example: Complete Tauri Integration

Here's a complete example of integrating a Tauri application with the FastAPI Agent Backend:

### FastAPI Backend Configuration (.env)

```
# API Configuration
HOST=0.0.0.0
PORT=8000

# Tauri Configuration
TAURI_ENABLED=true
TAURI_ALLOWED_ORIGINS=["tauri://localhost","tauri://your-app-name"]

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","tauri://localhost","tauri://your-app-name"]

# Other configuration options...
```

### Tauri Application Code (main.js)

```javascript
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { fetch } from '@tauri-apps/api/http';

function App() {
  const [task, setTask] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setLoading(true);
    try {
      const result = await fetch('http://localhost:8000/v1/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer your-auth-token'
        },
        body: JSON.stringify({
          task: task,
          agent_type: 'openai'
        })
      });
      
      setResponse(result.data.result);
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>AI Assistant</h1>
      <textarea 
        value={task} 
        onChange={(e) => setTask(e.target.value)} 
        placeholder="Enter your task here..."
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Processing...' : 'Submit'}
      </button>
      <div>
        <h2>Response:</h2>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default App;
```

## Next Steps

Once you've configured your Tauri integration, you can:

1. Develop your Tauri application UI
2. Implement authentication flow
3. Add more advanced features like streaming responses
4. Package your Tauri application for distribution

For more information on Tauri, see the [Tauri documentation](https://tauri.app/v1/guides/).