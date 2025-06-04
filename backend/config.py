from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///appDB.sqlite3"

    # For disabling CSRF in WTF forms (note the typo fix)
    WTF_CSRF_ENABLED = False    
    
    # Flask-Security / Flask-Security-Too settings
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret") 
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "default_salt")
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authorization"
    
    # Mail config
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    