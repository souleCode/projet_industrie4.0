import os
import requests
import json
from flask import Flask, request, jsonify

# Initialize the Flask app
app = Flask(__name__)

# Load config data
with open('config.json', 'r') as f:
    config = json.load(f)

SERVER_URL = config['server_url']
SECRET_KEY = config['secret_key']
PC_NAME = config['pc_name']
PC_IP = config['pc_ip']

# ==============================
# Generate JWT Token
# ==============================
def get_jwt_token():
    print("[INFO] Generating JWT Token...")
    try:
        response = requests.post(f"{SERVER_URL}/login", json={
            "username": "admin",
            "password": "admin"
        })
        if response.status_code == 200:
            token = response.json().get('token')
            print("[SUCCESS] Token generated successfully.")
            return token
        else:
            print("[ERROR] Failed to generate token:", response.json())
            return None
    except Exception as e:
        print(f"[ERROR] Connection error during token generation: {e}")
        return None

# ==============================
# Check Registration with Server 
# ==============================
def is_registered():
    print("[INFO] Checking if already registered with the server...")
    try:
        response = requests.get(f"{SERVER_URL}/list-pcs", headers={
            'Authorization': f'Bearer {get_jwt_token()}'
        })
        
        if response.status_code == 200:
            pcs = response.json()
            for pc in pcs:
                if pc['ip'] == PC_IP and pc['name'] == PC_NAME:
                    print("[INFO] This PC is already registered on the server.")
                    return True
            print("[INFO] PC not found on the server. Needs registration.")
            return False
        else:
            print(f"[ERROR] Could not fetch PC list: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] Connection error during registration check: {e}")
        return False

# ==============================
# Register with the Server
# ==============================
def register_with_server():
    if is_registered():
        return  # Skip registration if already registered

    print("[INFO] Registering with the server...")
    jwt_token = get_jwt_token()
    if not jwt_token:
        print("[ERROR] Registration aborted due to missing token.")
        return

    data = {
        "name": PC_NAME,
        "ip": PC_IP
    }

    try:
        response = requests.post(f"{SERVER_URL}/register-pc", json=data, headers={
            'Authorization': f'Bearer {jwt_token}'
        })
        if response.status_code == 201:
            print("[SUCCESS] Registered successfully with the server!")
        else:
            print(f"[ERROR] Failed to register: {response.json()}")
    except Exception as e:
        print(f"[ERROR] Connection error during registration: {e}")


# ==============================
# Status Endpoint
# ==============================
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": f"{PC_NAME} is online"}), 200

# ==============================
# Shutdown Listener Endpoint
# ==============================
@app.route('/shutdown', methods=['POST'])
def shutdown():
    secret_key = request.headers.get('Authorization')
    
    if secret_key == f"Bearer {SECRET_KEY}":
        print("[INFO] Shutdown command received. Executing...")
        os.system('shutdown /s /t 0')
        return jsonify({'message': 'Shutdown command executed'}), 200
    else:
        print("[WARNING] Unauthorized access attempt.")
        return jsonify({'error': 'Unauthorized'}), 401


# Simple health-check route
@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'client Server is running'}), 200

# ==============================
# Start the Client Listener
# ==============================
if __name__ == "__main__":
    print("[INFO] Listening for shutdown commands...")
    register_with_server()
    app.run(host='0.0.0.0', port=5001, debug=True)
