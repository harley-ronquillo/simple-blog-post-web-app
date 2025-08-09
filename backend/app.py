from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from config import Config
import os

def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow requests from any origin
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize config
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Database connection
    def get_db():
        return mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    
    # Make get_db available to routes
    app.get_db = get_db
    
    # Initialize database
    def init_db():
        try:
            # First, create the database if it doesn't exist
            conn = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD']
            )
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
            cursor.execute(f"USE {app.config['MYSQL_DB']}")
            
            # Check if users table exists and get its columns
            cursor.execute("SHOW TABLES LIKE 'users'")
            users_table_exists = cursor.fetchone() is not None
            
            if users_table_exists:
                # Check if has_selected_genres column exists
                cursor.execute("SHOW COLUMNS FROM users LIKE 'has_selected_genres'")
                has_column = cursor.fetchone() is not None
                
                if not has_column:
                    print("Adding has_selected_genres column to users table...")
                    cursor.execute('''
                        ALTER TABLE users 
                        ADD COLUMN has_selected_genres BOOLEAN DEFAULT FALSE
                    ''')
                    conn.commit()
            else:
                # Create users table with all columns
                cursor.execute('''
                    CREATE TABLE users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        has_selected_genres BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
            # Create genres table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS genres (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL
                )
            ''')
            
            # Create user_genres table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_genres (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    genre_id INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (genre_id) REFERENCES genres(id),
                    UNIQUE KEY unique_user_genre (user_id, genre_id)
                )
            ''')
            
            # Insert default genres
            default_genres = [
                'Technology', 'Science', 'Arts', 'Literature', 
                'Music', 'Travel', 'Food', 'Sports', 'Gaming',
                'Movies', 'Politics', 'Health', 'Education'
            ]
            
            for genre in default_genres:
                try:
                    cursor.execute('INSERT INTO genres (name) VALUES (%s)', (genre,))
                except mysql.connector.IntegrityError:
                    # Genre already exists
                    pass
            
            # Update has_selected_genres for existing users based on user_genres
            cursor.execute('''
                UPDATE users u 
                SET has_selected_genres = EXISTS (
                    SELECT 1 FROM user_genres ug 
                    WHERE ug.user_id = u.id 
                    GROUP BY ug.user_id 
                    HAVING COUNT(*) >= 3
                )
                WHERE has_selected_genres IS NULL
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("Database initialized successfully!")
            
        except mysql.connector.Error as err:
            print(f"Database initialization error: {err}")
            raise
    
    # Initialize database tables
    with app.app_context():
        init_db()
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.genres import genres_bp
    from routes.posts import posts_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(genres_bp, url_prefix='/genres')
    app.register_blueprint(posts_bp, url_prefix='/posts')
    
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Create data/posts directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'posts'), exist_ok=True)
    app.run(debug=True) 