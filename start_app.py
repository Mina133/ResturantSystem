#!/usr/bin/env python3
"""
Startup script for cPanel deployment
نظام إدارة المطاعم المحسن - سكريبت بدء التشغيل لنشر التطبيق على cPanel
"""

import os
import sys
import subprocess

def setup_environment():
    """إعداد بيئة التشغيل"""
    # Add project directories to Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, 'src')
    
    sys.path.insert(0, project_dir)
    sys.path.insert(0, src_dir)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    # Ensure database directory exists
    db_dir = os.path.join(src_dir, 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    print("Environment setup completed successfully")
    return True

def install_requirements():
    """تثبيت المتطلبات"""
    try:
        requirements_file = 'requirements_production.txt'
        if os.path.exists(requirements_file):
            print(f"Installing requirements from {requirements_file}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
            print("Requirements installed successfully")
        else:
            print("Requirements file not found, using basic requirements...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask', 'flask-cors'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("Starting Restaurant Management System...")
    print("بدء تشغيل نظام إدارة المطاعم...")
    
    # Setup environment
    if not setup_environment():
        print("Failed to setup environment")
        return False
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements")
        return False
    
    # Import and run the application
    try:
        from src.main import app, init_db
        
        # Initialize database
        print("Initializing database...")
        if init_db():
            print("Database initialized successfully")
        else:
            print("Database initialization failed")
        
        # Run the application
        print("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Application error: {e}")
        return False

if __name__ == '__main__':
    main()
