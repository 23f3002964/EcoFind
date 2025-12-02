from flask import Flask
from flask_cors import CORS
from backend.config import LocalDevelopmentConfig
from backend.models import db, User, Role
from backend.resource import api
from flask_security import Security, SQLAlchemyUserDatastore
from flask_mail import Mail

# Import blueprints
from backend.blueprints.auth import auth_bp, init_auth_blueprint
from backend.blueprints.products import products_bp
from backend.blueprints.users import users_bp
from backend.blueprints.admin import admin_bp
from backend.blueprints.cart import cart_bp
from backend.blueprints.misc import misc_bp
from backend.blueprints.messaging import messaging_bp
from backend.blueprints.reviews import reviews_bp

mail = Mail()

def createApp():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig) 
    CORS(app)
    db.init_app(app) # Initiating Model
    api.init_app(app) # Initiating Api
    mail.init_app(app) 
    datastore = SQLAlchemyUserDatastore(db, User, Role) # Create the user datastore
    app.security=Security(app, datastore, register_blueprint=False) # Initialize Flask-Security
    app.app_context().push()

    # Initialize blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(misc_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(reviews_bp)
    
    # Initialize auth blueprint with app and datastore
    init_auth_blueprint(app, datastore)

    return app

app = createApp()

import backend.create_initial_data
import backend.routes

if __name__ == "__main__":
    app.run(debug=True)