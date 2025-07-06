import os
import sys
from flask import Flask, send_from_directory, jsonify
from src.models.user import db
from src.routes.user import user_bp

# Path configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = '9IpDjXzQ9EgYNMh9pbEkmEk3c-PrhqudOrCGdRIgygA'

# =============================================================
# DATABASE CONFIGURATION - CORRECTED FORMAT
# =============================================================
# IMPORTANT: Database URL must be a single continuous string
app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://neonadsai_user:7ZC6K1S5Fu9PNh4yPGi9YUDYVpJoC1GI@dpg-d1kqvundiees73et2080-a.frankfurt-postgres.render.com:5432/neonadsai"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# =============================================================
# DATABASE INITIALIZATION WITH ERROR HANDLING
# =============================================================
def initialize_database():
    """Safe database initialization with error handling and logging"""
    try:
        with app.app_context():
            print("Attempting to connect to database...")
            print(f"Using database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Test connection first
            connection = db.engine.connect()
            connection.close()
            print("Database connection successful!")
            
            # Create tables
            db.create_all()
            print("Database tables created successfully")
            
        return True
    except Exception as e:
        print(f"!!! DATABASE INITIALIZATION FAILED !!!")
        print(f"Error: {str(e)}")
        print("Please verify your database configuration")
        return False

# Initialize database during app startup
initialize_database()

# =============================================================
# BLUEPRINT REGISTRATION
# =============================================================
app.register_blueprint(user_bp, url_prefix='/api')

# =============================================================
# HEALTH CHECK ENDPOINT
# =============================================================
@app.route('/health')
def health_check():
    """Endpoint to verify database connectivity"""
    try:
        # Simple database check
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'app': 'neonadsai-backend'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'connection failed',
            'error': str(e)
        }), 500

# =============================================================
# STATIC FILE SERVING (REACT APP)
# =============================================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# =============================================================
# APPLICATION STARTUP
# =============================================================
if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Debug mode based on environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"Starting neonadsai backend on port {port} (debug: {debug_mode})")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
