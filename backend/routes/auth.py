from flask import Blueprint, request, jsonify, current_app
import bcrypt
import jwt
import mysql.connector
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split('Bearer ')[1]
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = current_app.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, hashed_password)
            )
            conn.commit()
            
            # Get the created user
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            
            # Generate token
            token = jwt.encode({
                'user_id': user['id'],
                'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
            }, current_app.config['JWT_SECRET_KEY'])
            
            return jsonify({
                'message': 'User created successfully',
                'token': token,
                'user_id': user['id']
            }), 201
            
        except mysql.connector.IntegrityError as e:
            return jsonify({'message': 'Username or email already exists'}), 409
        except Exception as e:
            print(f"Error during signup: {str(e)}")
            return jsonify({'message': 'An error occurred during signup'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing signup request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'message': 'Missing required fields'}), 400
        
        conn = current_app.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                token = jwt.encode({
                    'user_id': user['id'],
                    'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
                }, current_app.config['JWT_SECRET_KEY'])
                
                return jsonify({
                    'message': 'Login successful',
                    'token': token,
                    'user_id': user['id']
                })
            else:
                return jsonify({'message': 'Invalid username or password'}), 401
                
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return jsonify({'message': 'An error occurred during login'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing login request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500 