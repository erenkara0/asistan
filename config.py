import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    
    # Connection Pool Settings
    DB_MIN_CONNECTIONS = int(os.getenv("DB_MIN_CONNECTIONS", "1"))
    DB_MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", "20"))
    DB_CONNECTION_TIMEOUT = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))
    DB_COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "60"))
    
    # Application Settings
    APP_ENV = os.getenv("APP_ENV", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_QUERY_RESULTS = int(os.getenv("MAX_QUERY_RESULTS", "500"))
    
    # Security Settings
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    @property
    def is_production(self):
        return self.APP_ENV == "production"
    
    @property
    def is_development(self):
        return self.APP_ENV == "development"
    
    def get_database_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Global config instance
config = Config()

# Production ayarları için örnek
"""
Production .env dosyası örneği:

DB_HOST=production-db-host.amazonaws.com
DB_PORT=5432
DB_USER=production_user
DB_PASSWORD=super_secure_password
DB_NAME=hotel_analytics
DB_MIN_CONNECTIONS=5
DB_MAX_CONNECTIONS=50
DB_CONNECTION_TIMEOUT=30
DB_COMMAND_TIMEOUT=60
APP_ENV=production
LOG_LEVEL=INFO
MAX_QUERY_RESULTS=500
MAX_MESSAGE_LENGTH=1000
OPENAI_API_KEY=your_openai_api_key_here
""" 