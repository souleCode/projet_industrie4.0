from flask import Flask, render_template, jsonify
from flask_cors import CORS
from routes import shutdown_routes
from auth_routes import auth_routes
from auth import jwt

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)
# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

# Initialize JWT
jwt.init_app(app)

# Register Blueprints (routes)
app.register_blueprint(shutdown_routes)
app.register_blueprint(auth_routes)

# Serve the Dashboard
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
