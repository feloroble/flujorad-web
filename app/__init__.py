from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.views.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
