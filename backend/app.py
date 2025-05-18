# app.py
from flask import Flask
from datetime import timedelta
import os
from extensions import db, login_manager, cors

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///ecofinds.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Initialize extensions with app
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)
    
    # Initialize Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Import and register routes
    with app.app_context():
        # Import models here to avoid circular imports
        import models
        from routes import register_routes
        register_routes(app)
        db.create_all()
        print("Database tables created successfully")
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
