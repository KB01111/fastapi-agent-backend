import streamlit as st
import os
import json
from dotenv import load_dotenv, set_key, find_dotenv

# Set page configuration
st.set_page_config(
    page_title="FastAPI Agent Backend - Admin Panel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load environment variables from .env file
def load_env_vars():
    # Load environment variables from .env file
    dotenv_path = find_dotenv()
    if not dotenv_path:
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if not os.path.exists(dotenv_path):
            # Create empty .env file if it doesn't exist
            with open(dotenv_path, "w") as f:
                pass

    load_dotenv(dotenv_path)
    return dotenv_path

# Function to save environment variables to .env file
def save_env_var(key, value, dotenv_path):
    set_key(dotenv_path, key, str(value))
    st.success(f"Saved {key} = {value}")

# Load environment variables
dotenv_path = load_env_vars()

# Main title
st.title("🤖 FastAPI Agent Backend - Admin Panel")
st.markdown("Configure your FastAPI Agent Backend settings through this user-friendly interface.")

# Sidebar navigation
st.sidebar.title("Configuration Sections")
section = st.sidebar.radio(
    "Select a section to configure:",
    [
        "API Configuration",
        "Authentication (Clerk)",
        "Database (Supabase)",
        "AI Configuration",
        "MindsDB Configuration",
        "Gmail Configuration",
        "CORS Configuration",
        "Tauri Configuration",
        "Observability",
        "Gunicorn Configuration",
        "Grafana Configuration"
    ]
)

# API Configuration
if section == "API Configuration":
    st.header("API Configuration")
    st.markdown("Configure basic API settings like debug mode, log level, host, and port.")

    col1, col2 = st.columns(2)

    with col1:
        debug = st.checkbox("Debug Mode", value=os.getenv("DEBUG", "false").lower() == "true")
        if st.button("Save Debug Mode"):
            save_env_var("DEBUG", str(debug).lower(), dotenv_path)

        host = st.text_input("Host", value=os.getenv("HOST", "0.0.0.0"))
        if st.button("Save Host"):
            save_env_var("HOST", host, dotenv_path)

    with col2:
        log_level = st.selectbox(
            "Log Level",
            ["debug", "info", "warning", "error", "critical"],
            index=["debug", "info", "warning", "error", "critical"].index(os.getenv("LOG_LEVEL", "info").lower())
        )
        if st.button("Save Log Level"):
            save_env_var("LOG_LEVEL", log_level, dotenv_path)

        port = st.number_input("Port", min_value=1, max_value=65535, value=int(os.getenv("PORT", "8000")))
        if st.button("Save Port"):
            save_env_var("PORT", str(port), dotenv_path)

# Authentication (Clerk)
elif section == "Authentication (Clerk)":
    st.header("Authentication (Clerk)")
    st.markdown("Configure Clerk authentication settings.")

    clerk_secret_key = st.text_input(
        "Clerk Secret Key",
        value=os.getenv("CLERK_SECRET_KEY", ""),
        type="password"
    )
    if st.button("Save Clerk Secret Key"):
        save_env_var("CLERK_SECRET_KEY", clerk_secret_key, dotenv_path)

    clerk_publishable_key = st.text_input(
        "Clerk Publishable Key",
        value=os.getenv("CLERK_PUBLISHABLE_KEY", "")
    )
    if st.button("Save Clerk Publishable Key"):
        save_env_var("CLERK_PUBLISHABLE_KEY", clerk_publishable_key, dotenv_path)

    jwt_algorithm = st.selectbox(
        "JWT Algorithm",
        ["RS256", "HS256"],
        index=["RS256", "HS256"].index(os.getenv("JWT_ALGORITHM", "RS256"))
    )
    if st.button("Save JWT Algorithm"):
        save_env_var("JWT_ALGORITHM", jwt_algorithm, dotenv_path)

# Database (Supabase)
elif section == "Database (Supabase)":
    st.header("Database (Supabase)")
    st.markdown("Configure Supabase database connection settings.")

    supabase_url = st.text_input(
        "Supabase URL",
        value=os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    )
    if st.button("Save Supabase URL"):
        save_env_var("SUPABASE_URL", supabase_url, dotenv_path)

    supabase_anon_key = st.text_input(
        "Supabase Anon Key",
        value=os.getenv("SUPABASE_ANON_KEY", ""),
        type="password"
    )
    if st.button("Save Supabase Anon Key"):
        save_env_var("SUPABASE_ANON_KEY", supabase_anon_key, dotenv_path)

    supabase_service_role_key = st.text_input(
        "Supabase Service Role Key",
        value=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        type="password"
    )
    if st.button("Save Supabase Service Role Key"):
        save_env_var("SUPABASE_SERVICE_ROLE_KEY", supabase_service_role_key, dotenv_path)

    database_url = st.text_input(
        "Database URL",
        value=os.getenv("DATABASE_URL", "postgresql://postgres:password@db.your-project.supabase.co:5432/postgres")
    )
    if st.button("Save Database URL"):
        save_env_var("DATABASE_URL", database_url, dotenv_path)

    st.markdown("---")
    st.subheader("Advanced Supabase Connection Settings")
    st.markdown("These settings are recommended for production deployments and remote connections.")

    supabase_direct_url = st.text_input(
        "Supabase Direct URL (for direct connections)",
        value=os.getenv("SUPABASE_DIRECT_URL", "")
    )
    if st.button("Save Supabase Direct URL"):
        save_env_var("SUPABASE_DIRECT_URL", supabase_direct_url, dotenv_path)

    supabase_connection_pooling = st.checkbox(
        "Enable Supabase Connection Pooling",
        value=os.getenv("SUPABASE_CONNECTION_POOLING", "true").lower() == "true"
    )
    if st.button("Save Supabase Connection Pooling"):
        save_env_var("SUPABASE_CONNECTION_POOLING", str(supabase_connection_pooling).lower(), dotenv_path)

# AI Configuration
elif section == "AI Configuration":
    st.header("AI Configuration")
    st.markdown("Configure AI provider API keys.")

    openai_api_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password"
    )
    if st.button("Save OpenAI API Key"):
        save_env_var("OPENAI_API_KEY", openai_api_key, dotenv_path)

    anthropic_api_key = st.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password"
    )
    if st.button("Save Anthropic API Key"):
        save_env_var("ANTHROPIC_API_KEY", anthropic_api_key, dotenv_path)

# MindsDB Configuration
elif section == "MindsDB Configuration":
    st.header("MindsDB Configuration")
    st.markdown("Configure MindsDB integration settings.")

    mindsdb_enabled = st.checkbox(
        "Enable MindsDB Integration",
        value=os.getenv("MINDSDB_ENABLED", "false").lower() == "true"
    )
    if st.button("Save MindsDB Enabled"):
        save_env_var("MINDSDB_ENABLED", str(mindsdb_enabled).lower(), dotenv_path)

    if mindsdb_enabled:
        col1, col2 = st.columns(2)

        with col1:
            mindsdb_host = st.text_input(
                "MindsDB Host",
                value=os.getenv("MINDSDB_HOST", "your-mindsdb-host.com")
            )
            if st.button("Save MindsDB Host"):
                save_env_var("MINDSDB_HOST", mindsdb_host, dotenv_path)

            mindsdb_user = st.text_input(
                "MindsDB User",
                value=os.getenv("MINDSDB_USER", "")
            )
            if st.button("Save MindsDB User"):
                save_env_var("MINDSDB_USER", mindsdb_user, dotenv_path)

        with col2:
            mindsdb_port = st.number_input(
                "MindsDB Port",
                min_value=1,
                max_value=65535,
                value=int(os.getenv("MINDSDB_PORT", "47334"))
            )
            if st.button("Save MindsDB Port"):
                save_env_var("MINDSDB_PORT", str(mindsdb_port), dotenv_path)

            mindsdb_password = st.text_input(
                "MindsDB Password",
                value=os.getenv("MINDSDB_PASSWORD", ""),
                type="password"
            )
            if st.button("Save MindsDB Password"):
                save_env_var("MINDSDB_PASSWORD", mindsdb_password, dotenv_path)

        mindsdb_use_https = st.checkbox(
            "Use HTTPS for MindsDB",
            value=os.getenv("MINDSDB_USE_HTTPS", "true").lower() == "true"
        )
        if st.button("Save MindsDB Use HTTPS"):
            save_env_var("MINDSDB_USE_HTTPS", str(mindsdb_use_https).lower(), dotenv_path)

# Gmail Configuration
elif section == "Gmail Configuration":
    st.header("Gmail Configuration")
    st.markdown("Configure Gmail integration settings.")

    gmail_enabled = st.checkbox(
        "Enable Gmail Integration",
        value=os.getenv("GMAIL_ENABLED", "false").lower() == "true"
    )
    if st.button("Save Gmail Enabled"):
        save_env_var("GMAIL_ENABLED", str(gmail_enabled).lower(), dotenv_path)

    if gmail_enabled:
        gmail_client_id = st.text_input(
            "Gmail Client ID",
            value=os.getenv("GMAIL_CLIENT_ID", "")
        )
        if st.button("Save Gmail Client ID"):
            save_env_var("GMAIL_CLIENT_ID", gmail_client_id, dotenv_path)

        gmail_client_secret = st.text_input(
            "Gmail Client Secret",
            value=os.getenv("GMAIL_CLIENT_SECRET", ""),
            type="password"
        )
        if st.button("Save Gmail Client Secret"):
            save_env_var("GMAIL_CLIENT_SECRET", gmail_client_secret, dotenv_path)

        gmail_refresh_token = st.text_input(
            "Gmail Refresh Token",
            value=os.getenv("GMAIL_REFRESH_TOKEN", ""),
            type="password"
        )
        if st.button("Save Gmail Refresh Token"):
            save_env_var("GMAIL_REFRESH_TOKEN", gmail_refresh_token, dotenv_path)

# CORS Configuration
elif section == "CORS Configuration":
    st.header("CORS Configuration")
    st.markdown("Configure Cross-Origin Resource Sharing (CORS) settings.")

    # Parse CORS origins from environment variable
    try:
        cors_origins = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:19006", "tauri://localhost", "tauri://*"]'))
    except json.JSONDecodeError:
        cors_origins = ["http://localhost:3000", "http://localhost:19006", "tauri://localhost", "tauri://*"]

    # Display current origins
    st.subheader("Current CORS Origins")
    for i, origin in enumerate(cors_origins):
        st.text(f"{i+1}. {origin}")

    # Add new origin
    st.subheader("Add New Origin")
    new_origin = st.text_input("New Origin URL (e.g., https://example.com)")
    if st.button("Add Origin") and new_origin:
        if new_origin not in cors_origins:
            cors_origins.append(new_origin)
            save_env_var("CORS_ORIGINS", json.dumps(cors_origins), dotenv_path)

    # Remove origin
    st.subheader("Remove Origin")
    origin_to_remove = st.selectbox("Select Origin to Remove", cors_origins)
    if st.button("Remove Origin") and origin_to_remove:
        cors_origins.remove(origin_to_remove)
        save_env_var("CORS_ORIGINS", json.dumps(cors_origins), dotenv_path)

    # Quick add for Tauri
    st.subheader("Quick Add for Tauri")
    if st.button("Add Tauri Origins"):
        tauri_origins = ["tauri://localhost", "tauri://*"]
        for origin in tauri_origins:
            if origin not in cors_origins:
                cors_origins.append(origin)
        save_env_var("CORS_ORIGINS", json.dumps(cors_origins), dotenv_path)

# Observability
elif section == "Observability":
    st.header("Observability")
    st.markdown("Configure monitoring and observability settings.")

    prometheus_port = st.number_input(
        "Prometheus Port",
        min_value=1,
        max_value=65535,
        value=int(os.getenv("PROMETHEUS_PORT", "8001"))
    )
    if st.button("Save Prometheus Port"):
        save_env_var("PROMETHEUS_PORT", str(prometheus_port), dotenv_path)

# Gunicorn Configuration
elif section == "Gunicorn Configuration":
    st.header("Gunicorn Configuration")
    st.markdown("Configure Gunicorn server settings.")

    gunicorn_workers = st.number_input(
        "Gunicorn Workers",
        min_value=1,
        max_value=32,
        value=int(os.getenv("GUNICORN_WORKERS", "4"))
    )
    if st.button("Save Gunicorn Workers"):
        save_env_var("GUNICORN_WORKERS", str(gunicorn_workers), dotenv_path)

# Tauri Configuration
elif section == "Tauri Configuration":
    st.header("Tauri Configuration")
    st.markdown("Configure Tauri desktop application integration settings.")

    tauri_enabled = st.checkbox(
        "Enable Tauri Integration",
        value=os.getenv("TAURI_ENABLED", "false").lower() == "true"
    )
    if st.button("Save Tauri Enabled"):
        save_env_var("TAURI_ENABLED", str(tauri_enabled).lower(), dotenv_path)

    if tauri_enabled:
        # Parse Tauri allowed origins from environment variable
        try:
            tauri_allowed_origins = json.loads(os.getenv("TAURI_ALLOWED_ORIGINS", '["tauri://localhost", "tauri://*"]'))
        except json.JSONDecodeError:
            tauri_allowed_origins = ["tauri://localhost", "tauri://*"]

        # Display current origins
        st.subheader("Tauri Allowed Origins")
        for i, origin in enumerate(tauri_allowed_origins):
            st.text(f"{i+1}. {origin}")

        # Add new origin
        st.subheader("Add New Tauri Origin")
        new_origin = st.text_input("New Tauri Origin (e.g., tauri://myapp)")
        if st.button("Add Tauri Origin") and new_origin:
            if new_origin not in tauri_allowed_origins:
                tauri_allowed_origins.append(new_origin)
                save_env_var("TAURI_ALLOWED_ORIGINS", json.dumps(tauri_allowed_origins), dotenv_path)

        # Remove origin
        st.subheader("Remove Tauri Origin")
        origin_to_remove = st.selectbox("Select Tauri Origin to Remove", tauri_allowed_origins)
        if st.button("Remove Tauri Origin") and origin_to_remove:
            tauri_allowed_origins.remove(origin_to_remove)
            save_env_var("TAURI_ALLOWED_ORIGINS", json.dumps(tauri_allowed_origins), dotenv_path)

        st.markdown("---")
        st.info("Make sure to also add these origins to your CORS Configuration to ensure proper communication between your Tauri app and the FastAPI backend.")

# Grafana Configuration
elif section == "Grafana Configuration":
    st.header("Grafana Configuration")
    st.markdown("Configure Grafana dashboard settings.")

    grafana_password = st.text_input(
        "Grafana Password",
        value=os.getenv("GRAFANA_PASSWORD", ""),
        type="password"
    )
    if st.button("Save Grafana Password"):
        save_env_var("GRAFANA_PASSWORD", grafana_password, dotenv_path)

# Footer
st.markdown("---")
st.markdown("FastAPI Agent Backend Admin Panel - Configure your application settings")
