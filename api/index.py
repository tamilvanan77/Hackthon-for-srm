import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit.web.bootstrap as bootstrap

def handler(event, context):
    """
    Vercel entry point for the Streamlit app.
    It calls streamlit's bootstrap to launch the app.py.
    """
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
    
    # We pass the sys.argv style arguments to streamlit
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    # Run the streamlit app
    bootstrap.run(app_path, "", [], [])

if __name__ == "__main__":
    # For local testing if needed
    handler(None, None)
