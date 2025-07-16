import os
from flask import Flask
from app.utils.mail import init_mail
from .extensions import db ,migrate , bcrypt, login_manager,csrf
from .models import register_models  # carga dinámica
from .routes import register_routes

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # Configuración
    app.config.from_object('app.config.DevelopmentConfig')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)  # <- IMPORTANTE
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configuración de correo
    app.config['MAIL_SERVER'] = 'mail.privateemail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = 'soporte@tecnotactil.com'
    app.config['MAIL_PASSWORD'] = 'XgPivL1YW1PFOKQ4mPhLZcurWmT8yc'
    app.config['MAIL_DEFAULT_SENDER'] = ('Tecno Táctil', 'soporte@tecnotactil.com')
    
    init_mail(app)
   
   # Cargar modelo User para LoginManager
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    login_manager.login_view = 'auth.login'

   
    # Registrar modelos automáticamente
    with app.app_context():
        register_models()
        db.create_all() # Crea las tablas en la base de datos
        
    # Registrar rutas
    register_routes(app)

    from flask import render_template

    @app.errorhandler(404)
    def pagina_no_encontrada(error):
      return render_template('error.html'), 404

    return app
