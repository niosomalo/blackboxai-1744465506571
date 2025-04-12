from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with SQLAlchemy"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
def reset_db(app):
    """Reset the database (for development purposes)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
