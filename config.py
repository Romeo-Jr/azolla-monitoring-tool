from os import environ

class Config:
    # CONFIGURATION FOR DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = environ.get("DB_URI")

    # CONFIGURATION FOR EMAIL
    MAIL_SERVER = environ.get("MAIL_SERVER")
    MAIL_PORT = environ.get("MAIL_PORT")
    MAIL_USE_TLS = True 
    MAIL_USERNAME = environ.get("MAIL_USERNAME") 
    MAIL_PASSWORD = environ.get("MAIL_PASSWORD") 
    MAIL_DEFAULT_SENDER = environ.get("MAIL_USERNAME")

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    DEBUG = False

config = {
    'default' : ProductionConfig,
    'production' : ProductionConfig
}