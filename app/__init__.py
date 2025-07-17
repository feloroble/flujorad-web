import os
import click
from flask import Flask, render_template
from dotenv import load_dotenv
from flask.cli import with_appcontext
from app.utils.mail import init_mail
from app.extensions import db, migrate, bcrypt, login_manager, csrf
from app.models import register_models
from app.routes import register_routes

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # Configuración
    app.config.from_object('app.config.DevelopmentConfig')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    init_mail(app)

    # Configuración correo
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'mail.privateemail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = (
        os.getenv('MAIL_SENDER_NAME', 'Tecno Táctil'),
        os.getenv('MAIL_USERNAME')
    )

    # Registrar modelos
    with app.app_context():
        register_models()
        db.create_all()

    # Login manager
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    login_manager.login_view = 'auth.login'

    # Rutas
    register_routes(app)

    # Página de error 404
    @app.errorhandler(404)
    def pagina_no_encontrada(error):
        return render_template('error.html'), 404

    # Comando custom para crear DB
    @app.cli.command("create-db")
    @with_appcontext
    def create_db():
        db.create_all()
        click.echo("Base de datos creada.")

    return app
