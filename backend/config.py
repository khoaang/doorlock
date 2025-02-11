import os
from datetime import timedelta


class Config:
    """Base configuration."""
    # Security
    SECRET_KEY = os.environ.get(
        'SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get(
        'JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_SECURE = False  # Set to True in production
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ERROR_MESSAGE_KEY = 'error'

    # Admin User
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@doorlock.local')
    ADMIN_PASSWORD = os.environ.get(
        'ADMIN_PASSWORD', 'admin123')  # Change in production!

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # API
    API_TITLE = 'DoorLock API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'
    API_SPEC_OPTIONS = {
        'security': [{'bearerAuth': []}],
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        }
    }

    # CORS
    # Add production URLs in production config
    CORS_ORIGINS = ['http://localhost:3000']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_EXPOSE_HEADERS = ['Content-Range', 'X-Total-Count']

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_HEADERS_ENABLED = True

    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'app.log'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 5

    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'py', 'sh', 'txt'}

    # WebSocket
    SOCKETIO_PING_TIMEOUT = 10
    SOCKETIO_PING_INTERVAL = 25
    SOCKETIO_ASYNC_MODE = 'eventlet'

    # Device Settings
    DEVICE_PING_TIMEOUT = 60  # seconds
    DEVICE_OFFLINE_THRESHOLD = 300  # seconds
    MAX_QUEUE_SIZE = 100  # maximum scripts in queue per device

    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    SQLALCHEMY_ECHO = True
    JWT_COOKIE_SECURE = False

    # Development-specific settings
    SEND_FILE_MAX_AGE_DEFAULT = 0
    TEMPLATES_AUTO_RELOAD = True

    # Mail settings for development
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    JWT_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False

    # Test-specific settings
    BCRYPT_LOG_ROUNDS = 4  # Lower for faster tests
    RATELIMIT_ENABLED = False
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql://doorlock:doorlock@db:5432/doorlock')

    # Override these in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_COOKIE_SECURE = True
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')

    # Production-specific settings
    RATELIMIT_STORAGE_URL = os.environ.get(
        'REDIS_URL', 'redis://redis:6379/0')
    LOG_LEVEL = 'ERROR'
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/1')

    # SSL/TLS Configuration
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Mail settings for production
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Monitoring and Performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }


class StagingConfig(ProductionConfig):
    """Staging configuration."""
    # Use a separate database for staging
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL')

    # Slightly more verbose logging than production
    LOG_LEVEL = 'WARNING'

    # Different Redis instance for staging
    RATELIMIT_STORAGE_URL = os.environ.get('STAGING_REDIS_URL')
    CACHE_REDIS_URL = os.environ.get('STAGING_REDIS_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}
