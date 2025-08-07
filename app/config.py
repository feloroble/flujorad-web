# config.py - Versión corregida y compatible
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno desde .env
load_dotenv() 

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'fdkgfsdkgsd45465464fsffeeter/**5/4fhfb6747//*'
    LALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de migraciones
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_timeout': 20,
        'echo': False,  # Cambiar a True para debug
        'connect_args': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': False,
            'sql_mode': 'TRADITIONAL,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
        }
    }
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENABLE_BLOG = True
    ENABLE_FLUJO_RAC = False
    APP_NAME = "Tecno Táctil"
    APP_VERSION = "1.0.0"
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'on']
    TOKEN_EXPIRATION = 3600  # 1 hora en segundos

    # Configuración de correo corregida
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_SENDER_NAME", "Tecno Táctil"),
        os.getenv("MAIL_USERNAME")
    )
    
    # Debug para mail (útil en desarrollo)
    MAIL_DEBUG = os.getenv("MAIL_DEBUG", "True").lower() == "true"

    # Configuraciones de seguridad para tokens
    SECURITY_SALT = os.getenv("SECURITY_SALT", "change_this_salt_in_production_12345")
    
    # Tiempos de expiración de tokens (en segundos)
    EMAIL_VERIFICATION_TOKEN_EXPIRY = int(os.getenv("EMAIL_VERIFICATION_TOKEN_EXPIRY", 86400))  # 24 horas
    PASSWORD_RESET_TOKEN_EXPIRY = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRY", 3600))  # 1 hora
    API_TOKEN_EXPIRY = int(os.getenv("API_TOKEN_EXPIRY", 2592000))  # 30 días
    
    # Configuración para rate limiting de tokens
    MAX_PASSWORD_RESET_ATTEMPTS = int(os.getenv("MAX_PASSWORD_RESET_ATTEMPTS", 5))
    PASSWORD_RESET_COOLDOWN = int(os.getenv("PASSWORD_RESET_COOLDOWN", 300))  # 5 minutos
    
    # URL base para links en correos
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    
    # Email del administrador para notificaciones
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    
    # Configuración de logging de seguridad
    SECURITY_LOG_LEVEL = os.getenv("SECURITY_LOG_LEVEL", "INFO")
    
    # Configuración JWT adicional
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 2592000))  # 30 días
    
    # Variable para identificar el entorno actual
    ENVIRONMENT = "base"
    
    @classmethod
    def get_config_info(cls):
        """Retorna información detallada de la configuración actual"""
        # Ocultar información sensible
        safe_db_uri = cls.SQLALCHEMY_DATABASE_URI
        if 'mysql://' in safe_db_uri and '@' in safe_db_uri:
            # Ocultar credenciales: mysql://user:pass@host/db -> mysql://***:***@host/db
            parts = safe_db_uri.split('@')
            if len(parts) >= 2:
                auth_part = parts[0].split('//')[-1]
                if ':' in auth_part:
                    safe_db_uri = safe_db_uri.replace(auth_part, '***:***')
        
        return {
            'environment': cls.ENVIRONMENT,
            'debug': getattr(cls, 'DEBUG', False),
            'testing': getattr(cls, 'TESTING', False),
            'app_name': cls.APP_NAME,
            'app_version': cls.APP_VERSION,
            'database_uri': safe_db_uri,
            'features': {
                'blog_enabled': cls.ENABLE_BLOG,
                'flujo_rac_enabled': cls.ENABLE_FLUJO_RAC,
            },
            'mail_config': {
                'server': cls.MAIL_SERVER,
                'port': cls.MAIL_PORT,
                'use_tls': cls.MAIL_USE_TLS,
                'username': cls.MAIL_USERNAME,
                'debug': cls.MAIL_DEBUG,
                'configured': cls.MAIL_USERNAME is not None
            },
            'tokens': {
                'email_verification_expiry': cls.EMAIL_VERIFICATION_TOKEN_EXPIRY,
                'password_reset_expiry': cls.PASSWORD_RESET_TOKEN_EXPIRY,
                'api_token_expiry': cls.API_TOKEN_EXPIRY,
                'max_reset_attempts': cls.MAX_PASSWORD_RESET_ATTEMPTS,
                'reset_cooldown': cls.PASSWORD_RESET_COOLDOWN
            },
            'security': {
                'base_url': cls.BASE_URL,
                'admin_email': cls.ADMIN_EMAIL,
                'security_salt_configured': len(cls.SECURITY_SALT) > 20
            }
        }
    
    @staticmethod
    def init_app(app):
        """Inicialización y verificación de la aplicación"""
        try:
            # Log de configuración aplicada
            environment = getattr(app.config, 'ENVIRONMENT', 'Unknown')
            app.logger.info(f"✅ Aplicación inicializada con configuración: {environment}")
            
            # Verificar configuraciones críticas
            Config._verify_critical_config(app)
            
        except Exception as e:
            app.logger.error(f"❌ Error en init_app: {str(e)}")
    
    @staticmethod
    def _verify_critical_config(app):
        """Verifica configuraciones críticas al iniciar"""
        warnings = []
        errors = []
        
        try:
            # Verificar SECRET_KEY
            if app.config.get('SECRET_KEY') == 'fdkgfsdkgsd454654646747//*':
                warnings.append("Usando SECRET_KEY por defecto - cambiar en producción")
            
            # Verificar configuración de correo
            if not app.config.get('MAIL_USERNAME'):
                warnings.append("MAIL_USERNAME no configurado - funciones de correo deshabilitadas")
            
            # Verificar SECURITY_SALT
            if app.config.get('SECURITY_SALT') == "change_this_salt_in_production_12345":
                warnings.append("Usando SECURITY_SALT por defecto - cambiar en producción")
            
            # Verificar BASE_URL en producción
            if not app.config.get('DEBUG', True) and app.config.get('BASE_URL') == "http://localhost:5000":
                errors.append("BASE_URL sigue apuntando a localhost en producción")
            
            # Log de advertencias y errores
            for warning in warnings:
                app.logger.warning(f"⚠️  CONFIG WARNING: {warning}")
            
            for error in errors:
                app.logger.error(f"❌ CONFIG ERROR: {error}")
            
            # No lanzar error por warnings, solo por errores críticos
            if errors and not app.config.get('DEBUG', False):
                raise RuntimeError(f"Errores críticos de configuración encontrados: {'; '.join(errors)}")
                
        except Exception as e:
            app.logger.error(f"❌ Error verificando configuración: {str(e)}")

class DevelopmentConfig(Config):
    DEBUG = True
    ENABLE_FLUJO_RAC = True
    ENVIRONMENT = "development"
    DATABASE_URL = os.environ.get('DATABASE_URL')


    # En desarrollo, tokens pueden durar más tiempo
    EMAIL_VERIFICATION_TOKEN_EXPIRY = 172800  # 48 horas
    PASSWORD_RESET_TOKEN_EXPIRY = 7200  # 2 horas

class ProductionConfig(Config):
    DEBUG = False
    ENABLE_FLUJO_RAC = False
    MAIL_DEBUG = False  # Desactivar debug de mail en producción
    ENVIRONMENT = "production"

    # Configuraciones adicionales de seguridad para producción
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'connect_args': {
            **Config.SQLALCHEMY_ENGINE_OPTIONS['connect_args'],
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'read_timeout': 60,
            'write_timeout': 60,
        }
    }

    # En producción, tokens deben ser más restrictivos
    EMAIL_VERIFICATION_TOKEN_EXPIRY = 43200  # 12 horas
    PASSWORD_RESET_TOKEN_EXPIRY = 1800  # 30 minutos
    
    # Rate limiting más estricto en producción
    MAX_PASSWORD_RESET_ATTEMPTS = 3
    PASSWORD_RESET_COOLDOWN = 600  # 10 minutos

class TestingConfig(Config):
    TESTING = True
    FLASK_ENV = 'testing'
    ENVIRONMENT = "testing"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # BD en memoria para tests

# Función para obtener configuración (compatible con tu código actual)
def get_config(config_name=None):
    """
    Función helper para obtener la clase de configuración
    Compatible con diferentes formas de importación
    """
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'default': DevelopmentConfig
    }
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    return configs.get(config_name, DevelopmentConfig)

# Para compatibilidad con tu código actual
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig, 
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# También exportar las clases directamente para flexibilidad
Development = DevelopmentConfig
Production = ProductionConfig
Testing = TestingConfig