#auth-service-- app.py

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app, supports_credentials=True)

# In-memory user storage with structure: {username: {'email': email, 'password': hashed_password}}
users = {}

@app.route('/signup', methods=['POST'])
def signup():
    data =request.json
    username=data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required fields'}), 400

    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    # Hash the password for security before storing
    hashed_password = generate_password_hash(password)

    # Store username, email, and hashed password
    users[username] = {
        'email': email,
        'password': hashed_password
    }

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username not in users or not check_password_hash(users[username]['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user'] = username
    return jsonify({'message': 'Logged in successfully'})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out successfully'})

# @app.route('/status', methods=['GET'])
# def status():
#     if 'user' in session:
#         return jsonify({'logged_in': True, 'user': session['user']})
#     return jsonify({'logged_in': False})
@app.route('/status', methods=['GET'])
def status():
    if 'user' in session:
        return jsonify({'logged_in': True, 'user': session['user'], 'email': users[session['user']]['email'], 'password': users[session['user']]['password']})
    return jsonify({'logged_in': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
