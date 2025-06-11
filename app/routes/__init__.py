from .main import main_bp
from .auth import auth_bp
from .user import user_bp
from .admin import admin_bp
from .flujorad import flujorad_bp

def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp) 
    app.register_blueprint(flujorad_bp)  # Descomentar si tienes admin_bp definido
    # Aquí puedes registrar más blueprints según sea necesario
