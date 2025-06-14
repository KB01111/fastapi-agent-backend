"""
Test script for the FastAPI Agent Backend Admin Panel.
This script verifies that the admin panel can read and write configuration settings.
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from dotenv import load_dotenv, find_dotenv, set_key

# Create a mock for streamlit since we can't actually run it in a test
class MockStreamlit:
    def __init__(self):
        self.title_text = None
        self.header_text = None
        self.markdown_text = []
        self.button_clicks = {}
        self.text_inputs = {}
        self.checkboxes = {}
        self.selectboxes = {}
        self.number_inputs = {}
        self.success_messages = []
    
    def title(self, text):
        self.title_text = text
    
    def header(self, text):
        self.header_text = text
    
    def markdown(self, text):
        self.markdown_text.append(text)
    
    def button(self, text):
        if text not in self.button_clicks:
            self.button_clicks[text] = False
        return self.button_clicks[text]
    
    def text_input(self, label, value="", type=None):
        if label not in self.text_inputs:
            self.text_inputs[label] = value
        return self.text_inputs[label]
    
    def checkbox(self, label, value=False):
        if label not in self.checkboxes:
            self.checkboxes[label] = value
        return self.checkboxes[label]
    
    def selectbox(self, label, options, index=0):
        if label not in self.selectboxes:
            self.selectboxes[label] = options[index]
        return self.selectboxes[label]
    
    def number_input(self, label, min_value=None, max_value=None, value=0):
        if label not in self.number_inputs:
            self.number_inputs[label] = value
        return self.number_inputs[label]
    
    def success(self, text):
        self.success_messages.append(text)
    
    def columns(self, n):
        return [self] * n
    
    def sidebar(self):
        return self
    
    def radio(self, label, options):
        return options[0]
    
    def set_page_config(self, **kwargs):
        pass


class TestAdminPanel(unittest.TestCase):
    """Test cases for the admin panel functionality."""
    
    def setUp(self):
        """Set up a temporary environment file for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env_path = os.path.join(self.temp_dir.name, ".env")
        
        # Create a test .env file
        with open(self.env_path, "w") as f:
            f.write("DEBUG=false\n")
            f.write("LOG_LEVEL=info\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=8000\n")
        
        # Set up environment variable to point to our test .env file
        os.environ["DOTENV_PATH"] = self.env_path
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
        if "DOTENV_PATH" in os.environ:
            del os.environ["DOTENV_PATH"]
    
    @patch("streamlit.title")
    @patch("streamlit.markdown")
    def test_admin_panel_loads(self, mock_markdown, mock_title):
        """Test that the admin panel loads without errors."""
        try:
            # Import the app module (this will execute the top-level code)
            from app import load_env_vars
            
            # Call the function to load environment variables
            dotenv_path = load_env_vars()
            
            # Check that the function returns a path
            self.assertIsNotNone(dotenv_path)
            
            # Check that the title was set
            mock_title.assert_called()
            
            # Check that markdown was used
            mock_markdown.assert_called()
            
            print("Admin panel loads successfully!")
        except Exception as e:
            self.fail(f"Admin panel failed to load: {e}")
    
    def test_save_env_var(self):
        """Test that the save_env_var function works correctly."""
        try:
            # Import the function from the app module
            from app import save_env_var
            
            # Create a mock streamlit instance
            st = MockStreamlit()
            
            # Call the function with a test key and value
            with patch("streamlit.success", st.success):
                save_env_var("TEST_KEY", "test_value", self.env_path)
            
            # Check that the environment variable was saved
            load_dotenv(self.env_path)
            self.assertEqual(os.getenv("TEST_KEY"), "test_value")
            
            # Check that a success message was displayed
            self.assertTrue(any("TEST_KEY" in msg for msg in st.success_messages))
            
            print("save_env_var function works correctly!")
        except Exception as e:
            self.fail(f"save_env_var test failed: {e}")


if __name__ == "__main__":
    unittest.main()