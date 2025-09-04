#!/usr/bin/env python3
"""
WSGI entry point for deployment platforms.
"""

import os
import sys
from pathlib import Path

# Add the web directory to Python path
web_dir = Path(__file__).parent / "web"
sys.path.insert(0, str(web_dir))

# Change to web directory
os.chdir(web_dir)

# Import the Flask app
from app import app as application

if __name__ == "__main__":
    application.run()
