from app.utils.activos import MODULOS_ACTIVOS




from .auth import auth_bp




def register_routes(app):
    app.register_blueprint(auth_bp)
    if 'user'  in MODULOS_ACTIVOS:
        from .user import user_bp
        app.register_blueprint(user_bp)
    if 'main'  in MODULOS_ACTIVOS:
        from .main import main_bp
        app.register_blueprint(main_bp)   
    if 'admin' in MODULOS_ACTIVOS:
        from .admin import admin_bp
        app.register_blueprint(admin_bp)
    if 'flujo_rac' in MODULOS_ACTIVOS:
        from .flujorad import flujorad_bp
        app.register_blueprint(flujorad_bp)
    
    
  
