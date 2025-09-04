#!/usr/bin/env python3
"""
Main application entry point for deployment platforms.
This file serves as a bridge to the actual web application.
"""

import os
import sys
from pathlib import Path

# Add the web directory to Python path
web_dir = Path(__file__).parent / "web"
sys.path.insert(0, str(web_dir))

# Change to web directory
os.chdir(web_dir)

# Import and run the actual Flask app
if __name__ == "__main__":
    from app import app
    print("🚀 Starting web application from root app.py...")
    print("📍 Web app will be available on the configured port")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5003)))
else:
    # For WSGI servers like Gunicorn
    from app import app as application
