"""
Configuration file for production deployment
نظام إدارة المطاعم المحسن - ملف الإعدادات لنشر التطبيق على cPanel
"""

import os

class Config:
    """إعدادات الإنتاج"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'arabic_restaurant_management_fixed_2024'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'src', 'database', 'restaurant_arabic_fixed.db')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS settings
    CORS_ORIGINS = ['*']  # Configure this for production
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'
    
    # Performance settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بالإعدادات"""
        pass

class DevelopmentConfig(Config):
    """إعدادات التطوير"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """إعدادات الإنتاج"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
