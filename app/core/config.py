import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration settings for the application.
    """
    # Application Settings
    APP_NAME = "General Institute System"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True") == "True"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # MongoDB Settings
    MONGO_CLUSTER_URL = os.getenv("MONGO_CLUSTER_URL")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE", "institute_db")
    
    # JWT Security
    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-minimum-32-characters")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "3000"))
    
    # Email Settings
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@institute.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_SERVER = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
    
    # CORS Settings
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://testfrontenda.vercel.app")
    
    @classmethod
    def get_allowed_origins_list(cls):
        """Convert ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in cls.ALLOWED_ORIGINS.split(",")]


config = Config()

# Validate configuration
if not config.JWT_SECRET_KEY or config.JWT_SECRET_KEY == "your-secret-key-change-this-in-production-minimum-32-characters":
    print("⚠️  WARNING: Using default SECRET_KEY. Please set a secure SECRET_KEY in .env file!")

if not config.MONGO_CLUSTER_URL:
    print("⚠️  WARNING: MONGO_CLUSTER_URL not set in .env file!")
