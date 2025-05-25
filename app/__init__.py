from flask import Flask
from config import Config
from .database import db





def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

   # Configurar MariaDB con Peewee
    

    
    # Manejar apertura/cierre de conexiones en cada request (Flask)
    @app.before_request
    def before_request():
        db.connect(reuse_if_open=True)  # Reusa conexiones existentes

    @app.teardown_request
    def teardown_request(exception):
        if not db.is_closed():
            db.close()

   

    from.models import Usuario  # Importar modelos para que Peewee los registre
    db.bind([Usuario])



    from app.views.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
