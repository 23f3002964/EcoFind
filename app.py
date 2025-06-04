from flask import Flask
from flask_cors import CORS
from backend.config import LocalDevelopmentConfig
from backend.models import db, User, Role
from backend.resource import api
from flask_security import Security, SQLAlchemyUserDatastore
from flask_mail import Mail

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

    return app

app = createApp()

import backend.create_initial_data
import backend.routes

if __name__ == "__main__":
    app.run(debug=True)