import os
import logging
import click
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from flask.cli import with_appcontext
from logging.handlers import RotatingFileHandler

# Importar configuración de forma segura
try:
    from . import config
    # Intentar importar el diccionario de configuraciones o las clases directamente
    if hasattr(config, 'config'):
        CONFIG_DICT = config.config
    else:
        # Crear diccionario de configuraciones si no existe
        CONFIG_DICT = {
            'development': getattr(config, 'DevelopmentConfig', getattr(config, 'Config', None)),
            'production': getattr(config, 'ProductionConfig', getattr(config, 'Config', None)),
            'testing': getattr(config, 'TestingConfig', getattr(config, 'Config', None))
        }
        # Filtrar valores None
        CONFIG_DICT = {k: v for k, v in CONFIG_DICT.items() if v is not None}
except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
    CONFIG_DICT = {}

from .extensions import db, migrate, bcrypt, login_manager, csrf
from .utils.mail import mail
from .models import register_models
from .routes import register_routes


# Cargar variables de entorno
load_dotenv()

def verify_database_connection():
    """Verificar conexión a base de datos compatible con SQLAlchemy 1.x y 2.x"""
    try:
        import sqlalchemy
        sqlalchemy_version = tuple(map(int, sqlalchemy.__version__.split('.')[:2]))
        
        if sqlalchemy_version >= (2, 0):
            from sqlalchemy import text
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
                return True
        else:
            db.engine.execute('SELECT 1')
            return True
    except Exception as e:
        return False

def configure_app(app, config_name=None):
    """Configurar la aplicación según el entorno"""
    try:
        # Corregir el typo en FLASK_CONFI -> FLASK_CONFIG
        config_name = config_name or os.getenv('FLASK_CONFIG', 'development')
        
        print(f"🔧 Configurando aplicación con entorno: {config_name}")
        
        # Método 1: Usar el diccionario de configuraciones
        if config_name in CONFIG_DICT and CONFIG_DICT[config_name]:
            config_class = CONFIG_DICT[config_name]
            app.config.from_object(config_class)
            print(f"✅ Configuración aplicada: {config_class.__name__}")
            
            # Inicializar configuración si tiene el método
            if hasattr(config_class, 'init_app'):
                try:
                    config_class.init_app(app)
                    print("✅ Configuración inicializada correctamente")
                except Exception as e:
                    print(f"⚠️  Error inicializando configuración: {e}")
            
            return config_class
            
        # Método 2: Fallback a configuración directa del módulo
        else:
            print(f"⚠️  Configuración '{config_name}' no encontrada, usando fallback...")
            
            # Mapeo de configuraciones como strings (tu método original)
            config_map = {
                'development': 'app.config.DevelopmentConfig',
                'production': 'app.config.ProductionConfig', 
                'testing': 'app.config.TestingConfig'
            }
            
            if config_name in config_map:
                try:
                    app.config.from_object(config_map[config_name])
                    print(f"✅ Configuración aplicada via string: {config_map[config_name]}")
                except Exception as e:
                    print(f"❌ Error con configuración string: {e}")
                    raise
            else:
                raise ValueError(f"Configuración '{config_name}' no reconocida")
                
    except Exception as e:
        print(f"❌ Error configurando aplicación: {e}")
        print("🔄 Aplicando configuración de desarrollo por defecto...")
        
        # Configuración de emergencia
        try:
            if hasattr(config, 'DevelopmentConfig'):
                app.config.from_object(config.DevelopmentConfig)
            elif hasattr(config, 'Config'):
                app.config.from_object(config.Config)
            else:
                # Configuración mínima de emergencia
                app.config.update({
                    'SECRET_KEY': os.environ.get('SECRET_KEY', 'emergency-key-change-immediately'),
                    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///emergency.db'),
                    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                    'DEBUG': True,
                    'APP_NAME': 'Tecno Táctil',
                    'APP_VERSION': '1.0.0'
                })
            print("✅ Configuración de emergencia aplicada")
        except Exception as emergency_error:
            print(f"❌ Error crítico en configuración de emergencia: {emergency_error}")
            raise


def validate_config(app):
    """Validar que las variables críticas estén configuradas"""
    required_vars = ['SECRET_KEY']
    missing_vars = []
    warnings = []
    
    for var in required_vars:
        if not app.config.get(var):
            missing_vars.append(var)
    
    # Verificaciones de seguridad adicionales
    if app.config.get('SECRET_KEY') in ['fdkgfsdkgsd454654646747//*', 'emergency-key-change-immediately']:
        warnings.append("SECRET_KEY usando valor por defecto - cambiar en producción")
    
    if app.config.get('SECURITY_SALT') == "change_this_salt_in_production_12345":
        warnings.append("SECURITY_SALT usando valor por defecto - cambiar en producción")
    
    # Log de advertencias
    for warning in warnings:
        app.logger.warning(f"⚠️  CONFIG WARNING: {warning}")
    
    if missing_vars:
        error_msg = f"Variables de configuración faltantes: {', '.join(missing_vars)}"
        app.logger.error(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
    
    print("✅ Validación de configuración completada")


def init_extensions(app):
    """Inicializar todas las extensiones de Flask"""
    try:
        print("🔌 Inicializando extensiones...")
        db.init_app(app)
        migrate.init_app(app, db)
        bcrypt.init_app(app)
        login_manager.init_app(app)
        csrf.init_app(app)
        mail.init_app(app)
        
        print("✅ Extensiones inicializadas correctamente")
    except Exception as e:
        print(f"❌ Error inicializando extensiones: {e}")
        raise


def configure_login_manager(app):
    """Configurar Flask-Login"""
    try:
        from app.models.user import User
        
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))
        
        login_manager.login_view = 'auth.login'
        login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
        login_manager.login_message_category = 'info'
        
        print("✅ Login manager configurado correctamente")
    except ImportError as e:
        print(f"⚠️  No se pudo importar User model: {e}")
    except Exception as e:
        print(f"❌ Error configurando login manager: {e}")


def init_database(app):
    """Inicializar base de datos"""
    try:
        with app.app_context():
            register_models()
            # Solo crear tablas automáticamente en desarrollo
            flask_env = app.config.get('FLASK_ENV') or app.config.get('ENVIRONMENT', 'development')
            if flask_env == 'development':
                db.create_all()
                print("✅ Base de datos inicializada (desarrollo)")
            else:
                print("ℹ️  Producción: usar migraciones para BD")
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        # No fallar completamente, solo logear el error
        app.logger.error(f"Database initialization error: {e}")


def configure_logging(app):
    """Configurar logging para producción"""
    try:
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
            
            app.logger.info('✅ Sistema de logging configurado para producción')
        else:
            print("📝 Modo desarrollo: logging en consola")
    except Exception as e:
        print(f"⚠️  Error configurando logging: {e}")


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
    
    print("✅ Manejadores de errores registrados")


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
    
    # Nuevos comandos para verificación de configuración
    @app.cli.command("show-config")
    @with_appcontext
    def show_config():
        """Mostrar configuración actual"""
        config_info = get_config_info(app)
        for key, value in config_info.items():
            click.echo(f"{key}: {value}")
    
    @app.cli.command("verify-config")
    @with_appcontext
    def verify_config():
        """Verificar configuración completa"""
        click.echo("=== VERIFICACIÓN DE CONFIGURACIÓN ===")
        
        config_info = get_config_info(app)
        click.echo(f"Entorno: {config_info.get('environment', 'unknown')}")
        click.echo(f"Debug: {config_info.get('debug', False)}")
        click.echo(f"Testing: {config_info.get('testing', False)}")
        
        # Verificar base de datos
        try:
            db.engine.execute('SELECT 1')
            click.echo("Base de datos: ✅ Conectada")
        except Exception as e:
            click.echo(f"Base de datos: ❌ Error - {e}")
        
        # Verificar correo
        mail_configured = bool(app.config.get('MAIL_USERNAME'))
        click.echo(f"Correo: {'✅ Configurado' if mail_configured else '❌ No configurado'}")
        
        # Features
        features = {
            'blog_enabled': app.config.get('ENABLE_BLOG', False),
            'flujo_rac_enabled': app.config.get('ENABLE_FLUJO_RAC', False),
            'mail_debug': app.config.get('MAIL_DEBUG', False)
        }
        
        click.echo("Features activas:")
        for feature, enabled in features.items():
            click.echo(f"  - {feature}: {'✅' if enabled else '❌'}")
    
    print("✅ Comandos CLI registrados")


def register_template_filters(app):
    """Registrar filtros personalizados para Jinja2"""
    
    @app.template_filter('currency')
    def currency_filter(amount):
        """Formatear cantidad como moneda"""
        return f"${amount:,.2f}" if amount else "$0.00"
    
    @app.template_filter('datetime')
    def datetime_filter(datetime_obj, format='%d/%m/%Y %H:%M'):
        """Formatear fecha y hora"""
        if datetime_obj is None:
            return ""
        return datetime_obj.strftime(format)
    
    print("✅ Filtros de template registrados")


def register_context_processors(app):
    """Registrar procesadores de contexto globales"""
    
    @app.context_processor
    def inject_config():
        """Inyectar configuración en todas las plantillas"""
        return {
            'app_name': app.config.get('APP_NAME', 'Tecno Táctil'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'environment': app.config.get('ENVIRONMENT') or app.config.get('FLASK_ENV', 'development')
        }
    
    print("✅ Procesadores de contexto registrados")


def register_config_routes(app):
    """Registrar rutas para verificar configuración"""
    
    @app.route('/config/status')
    def config_status():
        """Endpoint para verificar estado de configuración"""
        try:
            config_info = get_config_info(app)
            return jsonify({
                'status': 'ok',
                'timestamp': str(config_info.get('timestamp')),
                'config': config_info
            })
        except Exception as e:
            return jsonify({
                'status': 'error', 
                'message': str(e)
            }), 500
    
    @app.route('/config/database')
    def config_database():
        """Endpoint para verificar conexión de BD"""
        try:
            db.engine.execute('SELECT 1')
            return jsonify({
                'status': 'success',
                'message': 'Conexión a BD exitosa',
                'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'No configurada'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error de conexión: {str(e)}'
            }), 500
    
    @app.route('/health')
    def health_check():
        """Endpoint básico de health check"""
        return jsonify({
            'status': 'healthy',
            'app_name': app.config.get('APP_NAME', 'Tecno Táctil'),
            'version': app.config.get('APP_VERSION', '1.0.0'),
            'environment': app.config.get('ENVIRONMENT') or app.config.get('FLASK_ENV', 'development')
        })
    
    print("✅ Rutas de configuración registradas")


def get_config_info(app):
    """Obtener información detallada de configuración"""
    from datetime import datetime
    
    # Ocultar información sensible de la URI de BD
    safe_db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'mysql://' in safe_db_uri and '@' in safe_db_uri:
        parts = safe_db_uri.split('@')
        if len(parts) >= 2:
            auth_part = parts[0].split('//')[-1]
            if ':' in auth_part:
                safe_db_uri = safe_db_uri.replace(auth_part, '***:***')
    
    return {
        'timestamp': datetime.now().isoformat(),
        'environment': app.config.get('ENVIRONMENT') or app.config.get('FLASK_ENV', 'development'),
        'debug': app.debug,
        'testing': app.testing,
        'app_name': app.config.get('APP_NAME', 'Tecno Táctil'),
        'app_version': app.config.get('APP_VERSION', '1.0.0'),
        'database_uri': safe_db_uri,
        'features': {
            'blog_enabled': app.config.get('ENABLE_BLOG', False),
            'flujo_rac_enabled': app.config.get('ENABLE_FLUJO_RAC', False),
            'mail_debug': app.config.get('MAIL_DEBUG', False)
        },
        'mail_config': {
            'server': app.config.get('MAIL_SERVER'),
            'port': app.config.get('MAIL_PORT'),
            'username': app.config.get('MAIL_USERNAME'),
            'configured': bool(app.config.get('MAIL_USERNAME'))
        },
        'security': {
            'base_url': app.config.get('BASE_URL'),
            'admin_email': app.config.get('ADMIN_EMAIL'),
            'secret_key_configured': bool(app.config.get('SECRET_KEY')),
            'security_salt_configured': len(app.config.get('SECURITY_SALT', '')) > 20
        }
    }


def create_app(config_name=None):
    """Factory function para crear la aplicación Flask"""
    
    print("🚀 Iniciando creación de aplicación Flask...")
    
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
        register_config_routes(app)  # Nueva funcionalidad
        
        # Log de éxito
        environment = app.config.get('ENVIRONMENT') or app.config.get('FLASK_ENV', 'development')
        app.logger.info(f'✅ Aplicación creada correctamente en modo {environment}')
        print(f"✅ Aplicación Flask creada exitosamente - Entorno: {environment}")
        
        return app
        
    except Exception as e:
        # Si hay un error crítico durante la inicialización
        print(f"❌ Error crítico al crear la aplicación: {str(e)}")
        import traceback
        traceback.print_exc()
        raise