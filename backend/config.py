import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'blog_app')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours
    
    # Posts JSON Storage
    POSTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'posts')
    
    @staticmethod
    def init_app(app):
        # Create posts directory if it doesn't exist
        os.makedirs(Config.POSTS_DIR, exist_ok=True) 