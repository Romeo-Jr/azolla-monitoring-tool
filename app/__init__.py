from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail

from config import config

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config_name='production'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    from app.main import main, err, auth, api

    app.register_blueprint(main)
    app.register_blueprint(err)
    app.register_blueprint(auth)
    app.register_blueprint(api)
    
    return app