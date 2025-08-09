from flask import Blueprint, request, jsonify, current_app
from routes.auth import token_required
import mysql.connector

genres_bp = Blueprint('genres', __name__)

@genres_bp.route('', methods=['GET'])
@token_required
def get_genres(current_user):
    conn = current_app.get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('SELECT * FROM genres ORDER BY name')
        genres = cursor.fetchall()
        return jsonify(genres)
    except Exception as e:
        print(f"Error fetching genres: {str(e)}")
        return jsonify({'message': 'Error fetching genres'}), 500
    finally:
        cursor.close()
        conn.close()

@genres_bp.route('/user', methods=['GET'])
@token_required
def get_user_genres(current_user):
    conn = current_app.get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT g.* FROM genres g
            JOIN user_genres ug ON g.id = ug.genre_id
            WHERE ug.user_id = %s
            ORDER BY g.name
        ''', (current_user,))
        genres = cursor.fetchall()
        return jsonify(genres)
    except Exception as e:
        print(f"Error fetching user genres: {str(e)}")
        return jsonify({'message': 'Error fetching user genres'}), 500
    finally:
        cursor.close()
        conn.close()

@genres_bp.route('/user', methods=['POST'])
@token_required
def set_user_genres(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        genre_ids = data.get('genre_ids', [])
        
        if len(genre_ids) < 3:
            return jsonify({'message': 'Please select at least 3 genres'}), 400
        
        conn = current_app.get_db()
        cursor = conn.cursor()
        
        try:
            # Delete existing user genres
            cursor.execute('DELETE FROM user_genres WHERE user_id = %s', (current_user,))
            
            # Insert new user genres
            for genre_id in genre_ids:
                cursor.execute(
                    'INSERT INTO user_genres (user_id, genre_id) VALUES (%s, %s)',
                    (current_user, genre_id)
                )
            
            # Update user's genre selection status
            cursor.execute(
                'UPDATE users SET has_selected_genres = TRUE WHERE id = %s',
                (current_user,)
            )
            
            conn.commit()
            return jsonify({'message': 'User genres updated successfully'})
        except mysql.connector.Error as e:
            conn.rollback()
            print(f"Database error while updating user genres: {str(e)}")
            return jsonify({'message': 'Invalid genre selection'}), 400
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing genre update request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@genres_bp.route('/add', methods=['POST'])
@token_required
def add_genre(current_user):
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Genre name is required'}), 400
            
        genre_name = data['name'].strip()
        if not genre_name:
            return jsonify({'message': 'Genre name cannot be empty'}), 400
            
        conn = current_app.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Check if genre already exists
            cursor.execute('SELECT id FROM genres WHERE name = %s', (genre_name,))
            existing_genre = cursor.fetchone()
            
            if existing_genre:
                return jsonify({'message': 'Genre already exists'}), 409
                
            # Add new genre
            cursor.execute('INSERT INTO genres (name) VALUES (%s)', (genre_name,))
            genre_id = cursor.lastrowid
            
            # Add to user's genres
            cursor.execute(
                'INSERT INTO user_genres (user_id, genre_id) VALUES (%s, %s)',
                (current_user, genre_id)
            )
            
            conn.commit()
            return jsonify({
                'message': 'Genre added successfully',
                'genre': {
                    'id': genre_id,
                    'name': genre_name
                }
            }), 201
            
        except mysql.connector.Error as e:
            conn.rollback()
            print(f"Database error while adding genre: {str(e)}")
            return jsonify({'message': 'Error adding genre'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing add genre request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@genres_bp.route('/status', methods=['GET'])
@token_required
def get_genre_selection_status(current_user):
    conn = current_app.get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            'SELECT has_selected_genres FROM users WHERE id = %s',
            (current_user,)
        )
        result = cursor.fetchone()
        return jsonify({
            'has_selected_genres': bool(result['has_selected_genres'])
        })
    except Exception as e:
        print(f"Error fetching genre selection status: {str(e)}")
        return jsonify({'message': 'Error fetching status'}), 500
    finally:
        cursor.close()
        conn.close() 