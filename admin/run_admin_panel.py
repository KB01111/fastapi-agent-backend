"""
Startup script for the FastAPI Agent Backend Admin Panel.
This script runs the Streamlit application for the admin panel.
"""

import os
import subprocess
import sys

def main():
    """Run the Streamlit application for the admin panel."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the path to the app.py file
    app_path = os.path.join(script_dir, "app.py")
    
    # Check if the app.py file exists
    if not os.path.exists(app_path):
        print(f"Error: Could not find {app_path}")
        sys.exit(1)
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Error: Streamlit is not installed.")
        print("Please install it using: pip install streamlit")
        sys.exit(1)
    
    # Run the Streamlit application
    print("Starting FastAPI Agent Backend Admin Panel...")
    try:
        subprocess.run(["streamlit", "run", app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAdmin panel stopped.")

if __name__ == "__main__":
    main()