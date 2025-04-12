from flask import Flask, send_from_directory
from flask_cors import CORS
from database import init_db
from errors import init_error_handlers
from routes.bahan import bahan_bp
from routes.menu import menu_bp
from routes.penjualan import penjualan_bp
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='../frontend')
    
    # Enable CORS
    CORS(app)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe_inventory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    
    # Initialize error handlers
    init_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(bahan_bp, url_prefix='/api')
    app.register_blueprint(menu_bp, url_prefix='/api')
    app.register_blueprint(penjualan_bp, url_prefix='/api')
    
    # Serve frontend files
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(app.static_folder, path)
    
    # Add a health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Service is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
