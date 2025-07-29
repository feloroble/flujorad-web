import os
import logging
import click
from flask import Flask, render_template
from dotenv import load_dotenv
from flask.cli import with_appcontext
from logging.handlers import RotatingFileHandler

from app.utils.mail import init_mail
from app.extensions import db, migrate, bcrypt, login_manager, csrf
from app.models import register_models
from app.routes import register_routes

# Cargar variables de entorno
load_dotenv()


def configure_app(app, config_name=None):
    """Configurar la aplicación según el entorno"""
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': 'app.config.DevelopmentConfig',
        'production': 'app.config.ProductionConfig',
        'testing': 'app.config.TestingConfig'
    }
    
    config_class = config_map.get(config_name, config_map['development'])
    app.config.from_object(config_class)


def validate_config(app):
    """Validar que las variables críticas estén configuradas"""
    required_vars = ['SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not app.config.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise RuntimeError(f"Variables de configuración faltantes: {', '.join(missing_vars)}")


def init_extensions(app):
    """Inicializar todas las extensiones de Flask"""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    init_mail(app)


def configure_mail(app):
    """Configurar parámetros de correo desde variables de entorno"""
    mail_config = {
        'MAIL_SERVER': os.getenv('MAIL_SERVER', 'mail.privateemail.com'),
        'MAIL_PORT': int(os.getenv('MAIL_PORT', 465)),
        'MAIL_USE_SSL': os.getenv('MAIL_USE_SSL', 'False').lower() == 'true',
        'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'False').lower() == 'true',
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': (
            os.getenv('MAIL_SENDER_NAME', 'Tecno Táctil'),
            os.getenv('MAIL_USERNAME')
        )
    }
    
    app.config.update(mail_config)


def configure_login_manager(app):
    """Configurar Flask-Login"""
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'


def init_database(app):
    """Inicializar base de datos"""
    with app.app_context():
        register_models()
        # Solo crear tablas automáticamente en desarrollo
        if app.config.get('FLASK_ENV') == 'development':
            db.create_all()


def configure_logging(app):
    """Configurar logging para producción"""
    if not app.debug and not app.testing:
        # Crear directorio de logs si no existe
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configurar handler de archivos rotativos
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        # Formato de logs
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        
        app.logger.info('Aplicación iniciada correctamente')


def register_error_handlers(app):
    """Registrar manejadores de errores personalizados"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'Página no encontrada: {error}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Error interno del servidor: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'Acceso prohibido: {error}')
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f'Solicitud incorrecta: {error}')
        return render_template('errors/400.html'), 400


def register_cli_commands(app):
    """Registrar comandos CLI personalizados"""
    
    @app.cli.command("create-db")
    @with_appcontext
    def create_db():
        """Crear todas las tablas de la base de datos"""
        db.create_all()
        click.echo("✅ Base de datos creada correctamente.")
    
    @app.cli.command("drop-db")
    @with_appcontext
    def drop_db():
        """Eliminar todas las tablas de la base de datos"""
        if click.confirm('¿Estás seguro de que quieres eliminar toda la base de datos?'):
            db.drop_all()
            click.echo("❌ Base de datos eliminada.")
        else:
            click.echo("Operación cancelada.")
    
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        """Inicializar base de datos con datos de prueba"""
        db.create_all()
        # Aquí puedes agregar datos iniciales
        click.echo("🚀 Base de datos inicializada con datos de prueba.")


def register_template_filters(app):
    """Registrar filtros personalizados para Jinja2"""
    
    @app.template_filter('currency')
    def currency_filter(amount):
        """Formatear cantidad como moneda"""
        return f"${amount:,.2f}"
    
    @app.template_filter('datetime')
    def datetime_filter(datetime_obj, format='%d/%m/%Y %H:%M'):
        """Formatear fecha y hora"""
        if datetime_obj is None:
            return ""
        return datetime_obj.strftime(format)


def register_context_processors(app):
    """Registrar procesadores de contexto globales"""
    
    @app.context_processor
    def inject_config():
        """Inyectar configuración en todas las plantillas"""
        return {
            'app_name': app.config.get('APP_NAME', 'Tecno Táctil'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'environment': app.config.get('FLASK_ENV', 'development')
        }


def create_app(config_name=None):
    """Factory function para crear la aplicación Flask"""
    
    # Crear instancia de Flask
    app = Flask(__name__, 
                static_folder='static', 
                static_url_path='/static',
                instance_relative_config=True)
    
    try:
        # Configuración básica
        configure_app(app, config_name)
        validate_config(app)
        
        # Inicializar extensiones
        init_extensions(app)
        
        # Configuraciones específicas
        configure_mail(app)
        configure_login_manager(app)
        configure_logging(app)
        
        # Base de datos
        init_database(app)
        
        # Registrar componentes
        register_routes(app)
        register_error_handlers(app)
        register_cli_commands(app)
        register_template_filters(app)
        register_context_processors(app)
        
        app.logger.info(f'Aplicación creada correctamente en modo {app.config.get("FLASK_ENV", "development")}')
        
        return app
        
    except Exception as e:
        # Si hay un error crítico durante la inicialización
        print(f"❌ Error crítico al crear la aplicación: {str(e)}")
        raise