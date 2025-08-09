from flask import Blueprint, request, jsonify, current_app
from routes.auth import token_required
import json
import os
import time
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

def get_post_file_path(post_id):
    return os.path.join(current_app.config['POSTS_DIR'], f'{post_id}.json')

def generate_post_id():
    return str(int(time.time() * 1000))

@posts_bp.route('', methods=['POST'])
@token_required
def create_post(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        post_text = data.get('post_text')
        genre_id = data.get('genre_id')
        
        if not all([post_text, genre_id]):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Get genre name
        conn = current_app.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT name FROM genres WHERE id = %s', (genre_id,))
            genre = cursor.fetchone()
            
            if not genre:
                return jsonify({'message': 'Invalid genre'}), 400
            
            # Create post
            post_id = generate_post_id()
            post_data = {
                'id': post_id,
                'user_id': current_user,
                'post_text': post_text,
                'genre_id': genre_id,
                'genre_name': genre['name'],
                'created_at': datetime.utcnow().isoformat(),
                'up_vote_count': 0,
                'down_vote_count': 0,
                'share_count': 0,
                'comments': []
            }
            
            # Save post to JSON file
            post_file = get_post_file_path(post_id)
            with open(post_file, 'w') as f:
                json.dump(post_data, f, indent=2)
            
            return jsonify(post_data), 201
        except Exception as e:
            print(f"Error creating post: {str(e)}")
            return jsonify({'message': 'Error creating post'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing post creation request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@posts_bp.route('', methods=['GET'])
@token_required
def get_posts(current_user):
    try:
        # Get user's genre preferences
        conn = current_app.get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT genre_id FROM user_genres WHERE user_id = %s',
                (current_user,)
            )
            user_genres = [row[0] for row in cursor.fetchall()]
            
            # Get all posts from JSON files
            posts = []
            posts_dir = current_app.config['POSTS_DIR']
            
            if os.path.exists(posts_dir):
                for filename in os.listdir(posts_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(posts_dir, filename)) as f:
                                post = json.load(f)
                                # Only include posts from user's preferred genres
                                if int(post['genre_id']) in user_genres:
                                    posts.append(post)
                        except Exception as e:
                            print(f"Error reading post file {filename}: {str(e)}")
                            continue
            
            # Sort posts by creation date (newest first)
            posts.sort(key=lambda x: x['created_at'], reverse=True)
            return jsonify(posts)
            
        except Exception as e:
            print(f"Error fetching posts: {str(e)}")
            return jsonify({'message': 'Error fetching posts'}), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error processing get posts request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@posts_bp.route('/<post_id>/vote', methods=['POST'])
@token_required
def vote_post(current_user, post_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        vote_type = data.get('vote_type')
        
        if vote_type not in ['up', 'down']:
            return jsonify({'message': 'Invalid vote type'}), 400
        
        post_file = get_post_file_path(post_id)
        if not os.path.exists(post_file):
            return jsonify({'message': 'Post not found'}), 404
        
        try:
            with open(post_file, 'r+') as f:
                post = json.load(f)
                if vote_type == 'up':
                    post['up_vote_count'] += 1
                else:
                    post['down_vote_count'] += 1
                
                f.seek(0)
                json.dump(post, f, indent=2)
                f.truncate()
            
            return jsonify(post)
        except Exception as e:
            print(f"Error updating vote count: {str(e)}")
            return jsonify({'message': 'Error updating vote count'}), 500
            
    except Exception as e:
        print(f"Error processing vote request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@posts_bp.route('/<post_id>/share', methods=['POST'])
@token_required
def share_post(current_user, post_id):
    try:
        post_file = get_post_file_path(post_id)
        if not os.path.exists(post_file):
            return jsonify({'message': 'Post not found'}), 404
        
        try:
            with open(post_file, 'r+') as f:
                post = json.load(f)
                post['share_count'] += 1
                
                f.seek(0)
                json.dump(post, f, indent=2)
                f.truncate()
            
            return jsonify(post)
        except Exception as e:
            print(f"Error updating share count: {str(e)}")
            return jsonify({'message': 'Error updating share count'}), 500
            
    except Exception as e:
        print(f"Error processing share request: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500 