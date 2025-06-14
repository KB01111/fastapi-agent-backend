# FastAPI Agent Backend - Admin Control Panel

A Streamlit-based admin control panel for configuring the FastAPI Agent Backend.

## Overview

This admin panel provides a user-friendly interface for configuring the FastAPI Agent Backend without having to manually edit the `.env` file. It allows you to configure all aspects of the application, including:

- API Configuration
- Authentication (Clerk)
- Database (Supabase)
- AI Configuration
- MindsDB Integration
- Gmail Integration
- CORS Configuration
- Observability
- Gunicorn Configuration
- Grafana Configuration

## Installation

1. Make sure you have installed the required dependencies:

```bash
pip install streamlit python-dotenv
```

2. Navigate to the project root directory and run the admin panel using one of these methods:

**Option 1: Using the startup script (recommended)**
```bash
python admin/run_admin_panel.py
```

**Option 2: Using Streamlit directly**
```bash
streamlit run admin/app.py
```

## Usage

1. The admin panel will open in your default web browser.
2. Use the sidebar to navigate between different configuration sections.
3. Modify the settings as needed.
4. Click the "Save" button next to each setting to save it to the `.env` file.
5. The changes will take effect the next time you restart the FastAPI application.

## Testing

A test script is provided to verify that the admin panel works correctly:

```bash
python -m unittest admin.test_admin_panel
```

This script tests:
- That the admin panel loads without errors
- That the environment variables are correctly saved to the `.env` file

The tests use a temporary `.env` file, so they don't modify your actual configuration.

## Security Considerations

- The admin panel should only be run in a secure environment, as it provides access to sensitive configuration settings.
- Consider adding authentication to the Streamlit app in production environments.
- Never expose the admin panel to the public internet without proper security measures.

## Configuration Sections

### API Configuration
Configure basic API settings like debug mode, log level, host, and port.

### Authentication (Clerk)
Configure Clerk authentication settings, including secret keys and JWT algorithm.

### Database (Supabase)
Configure Supabase database connection settings, including URL and API keys.

### AI Configuration
Configure AI provider API keys for OpenAI and Anthropic.

### MindsDB Configuration
Configure MindsDB integration settings, including connection details and credentials.

### Gmail Configuration
Configure Gmail integration settings, including OAuth credentials.

### CORS Configuration
Configure Cross-Origin Resource Sharing (CORS) settings, including allowed origins.

### Observability
Configure monitoring and observability settings, including Prometheus port.

### Gunicorn Configuration
Configure Gunicorn server settings, including the number of workers.

### Grafana Configuration
Configure Grafana dashboard settings, including the admin password.
