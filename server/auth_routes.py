from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

auth_routes = Blueprint('auth_routes', __name__)

# ==============================
# Login Route (Admin Login)
# ==============================
@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'admin@admin' and data.get('password') == 'admin':
        token = create_access_token(identity=data['username'])
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
