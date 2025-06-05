import json
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

shutdown_routes = Blueprint('shutdown_routes', __name__)

def load_db():
    with open('db.json', 'r') as file:
        return json.load(file)

def save_db(data):
    with open('db.json', 'w') as file:
        json.dump(data, file, indent=4)

@shutdown_routes.route('/register-pc', methods=['POST'])
@jwt_required()
def register_pc():
    data = request.json
    db = load_db()
    db.append(data)
    save_db(db)
    return jsonify({'message': 'PC registered successfully!'}), 201

@shutdown_routes.route('/list-pcs', methods=['GET'])
@jwt_required()
def list_pcs():
    status_filter = request.args.get('status')
    db = load_db()
    
    if status_filter == 'online':
        pcs = [pc for pc in db if pc['status'] == 'online']
    elif status_filter == 'offline':
        pcs = [pc for pc in db if pc['status'] == 'offline']
    else:
        pcs = db
    
    return jsonify(pcs), 200

@shutdown_routes.route('/ping-pcs', methods=['GET'])
@jwt_required()
def ping_pcs():
    db = load_db()
    for pc in db:
        try:
            response = requests.get(f"http://{pc['ip']}:5001/status", timeout=3)
            pc['status'] = 'online' if response.status_code == 200 else 'offline'
        except requests.RequestException:
            pc['status'] = 'offline'
    save_db(db)
    return jsonify(db), 200

@shutdown_routes.route('/trigger-shutdown', methods=['POST'])
@jwt_required()
def trigger_shutdown():
    data = request.json
    pc_name = data.get('name')
    db = load_db()
    
    targets = [pc for pc in db if pc['status'] == 'online'] if pc_name == 'all' \
              else [pc for pc in db if (pc['name'] == pc_name or pc['ip'] == pc_name) and pc['status'] == 'online']
    
    for pc in targets:
        try:
            requests.post(
                f"http://{pc['ip']}:5001/shutdown",
                headers={'Authorization': 'Bearer your-secret-key'}
            )
        except Exception as e:
            print(f"Shutdown error for {pc['name']}: {e}")
    
    return jsonify({'message': f"Shutdown commands sent to {[t['name'] for t in targets]}"}), 200

@shutdown_routes.route('/shutdown-all-online', methods=['POST'])
@jwt_required()
def shutdown_all_online():
    db = load_db()
    online_pcs = [pc for pc in db if pc['status'] == 'online']
    
    for pc in online_pcs:
        try:
            requests.post(
                f"http://{pc['ip']}:5001/shutdown",
                headers={'Authorization': 'Bearer your-secret-key'}
            )
        except Exception as e:
            print(f"Shutdown error for {pc['name']}: {e}")
    
    return jsonify({'message': f"Shutdown commands sent to {[pc['name'] for pc in online_pcs]}"}), 200

@shutdown_routes.route('/schedule-shutdown', methods=['POST'])
@jwt_required()
def schedule_shutdown():
    # Implement your scheduling logic here
    return jsonify({'message': 'Shutdown scheduled successfully'}), 200
