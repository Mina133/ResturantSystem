#!/usr/bin/env python3
"""
Passenger WSGI file for cPanel deployment
نظام إدارة المطاعم المحسن - ملف Passenger WSGI لنشر التطبيق على cPanel
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Add src directory to Python path
src_dir = os.path.join(project_dir, 'src')
sys.path.insert(0, src_dir)

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import the Flask application
from src.main import app as application

# Ensure database is initialized
if __name__ == '__main__':
    # This will only run if the file is executed directly
    # In production, Passenger will handle this
    pass
