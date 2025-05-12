import os
import requests
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

shutdown_routes = Blueprint('shutdown_routes', __name__)

# Load the database
def load_db():
    with open('db.json', 'r') as file:
        return json.load(file)

def save_db(data):
    with open('db.json', 'w') as file:
        json.dump(data, file, indent=4)


# ==============================
# Register a new PC
@shutdown_routes.route('/register-pc', methods=['POST'])
@jwt_required()
def register_pc():
    data = request.json
    db = load_db()
    db.append(data)
    save_db(db)
    return jsonify({'message': 'PC registered successfully!'}), 201


# ==============================
# List all PCs and their statuses
@shutdown_routes.route('/list-pcs', methods=['GET'])
@jwt_required()
def list_pcs():
    db = load_db()
    return jsonify(db), 200


# ==============================
# Ping all PCs to check status
@shutdown_routes.route('/ping-pcs', methods=['GET'])
@jwt_required()
def ping_pcs():
    print("[INFO] Pinging all registered PCs...")
    db = load_db()
    for pc in db:
        try:
            print(f"[INFO] Pinging {pc['name']} at {pc['ip']}...")
            response = requests.get(f"http://{pc['ip']}:5001/status", timeout=3)
            if response.status_code == 200:
                pc['status'] = 'online'
                print(f"[SUCCESS] {pc['name']} is online.")
            else:
                pc['status'] = 'offline'
        except requests.RequestException as e:
            print(f"[ERROR] Could not reach {pc['name']}: {e}")
            pc['status'] = 'offline'
    
    save_db(db)
    return jsonify(db), 200



# ==============================
# Trigger shutdown for specific or all PCs
@shutdown_routes.route('/trigger-shutdown', methods=['POST'])
@jwt_required()
def trigger_shutdown():
    data = request.json
    pc_name = data.get('name')  # This is the name or IP provided for the shutdown command
    db = load_db()

    print(f"[INFO] Received shutdown command for: {pc_name}")
    print(f"[INFO] Registered PCs in DB: {db}")

    # Identify the PCs to shutdown
    if pc_name == 'all':
        targets = [pc for pc in db if pc['status'] == 'online']
    else:
        # Match by either name or IP address
        targets = [pc for pc in db if (pc['name'] == pc_name or pc['ip'] == pc_name) and pc['status'] == 'online']

    print(f"[INFO] Shutdown targets: {[pc['name'] for pc in targets]}")

    # Send shutdown requests to each target
    for pc in targets:
        try:
            print(f"[INFO] Sending shutdown request to {pc['name']} at {pc['ip']}...")
            response = requests.post(f"http://{pc['ip']}:5001/shutdown", headers={'Authorization': 'Bearer your-secret-key'})
            if response.status_code == 200:
                print(f"[SUCCESS] Shutdown command sent to {pc['name']}")
            else:
                print(f"[ERROR] Failed to send shutdown to {pc['name']}")
        except Exception as e:
            print(f"[ERROR] Could not shutdown {pc['name']}: {e}")

    # Return the result
    return jsonify({'message': f"Shutdown commands sent to {[t['name'] for t in targets]}"}), 200

# ==============================
# List all PCs and their statuses (filterable by status)
@shutdown_routes.route('/list-pcs', methods=['GET'], endpoint='list_pcs_status')
@jwt_required()
def list_pcs():
    status_filter = request.args.get('status')  # status parameter can be 'online', 'offline', or 'all'
    db = load_db()

    if status_filter == 'online':
        pcs = [pc for pc in db if pc['status'] == 'online']
    elif status_filter == 'offline':
        pcs = [pc for pc in db if pc['status'] == 'offline']
    else:
        pcs = db  # All PCs

    return jsonify(pcs), 200


# ==============================
# Shutdown all online PCs
@shutdown_routes.route('/shutdown-all-online', methods=['POST'])
@jwt_required()
def shutdown_all_online():
    db = load_db()
    online_pcs = [pc for pc in db if pc['status'] == 'online']

    for pc in online_pcs:
        try:
            requests.post(f"http://{pc['ip']}:5001/shutdown", headers={'Authorization': 'Bearer your-secret-key'})
        except Exception as e:
            print(f"[ERROR] Could not shutdown {pc['name']}: {e}")

    return jsonify({'message': f"Shutdown commands sent to {[pc['name'] for pc in online_pcs]}"}), 200
