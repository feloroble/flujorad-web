from datetime import datetime, timedelta

import bcrypt
from app.extensions import db
from flask_login import UserMixin



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' o 'user'
    profile_picture = db.Column(db.String(255), nullable=True)  # Ruta a la imagen

    is_admin = db.Column(db.Boolean, default=False, nullable=False)
   

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    phone = db.Column(db.String(20))
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(5), default='es')

    def is_admin(self):
        return self.role == 'admin'
    def is_admin_pago(self):
        return self.role == 'admin_pago'
    def is_user_TCP(self):
        return self.role == 'user_tcp'

    def is_user(self):
        return self.role == 'user'

    def __repr__(self):
        return f'<User {self.email}>'
    def set_password(self, password):
        """Establecer contraseña hasheada de forma segura"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """Verificar contraseña"""
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def verify_email(self):
        """Marcar email como verificado"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
    
    def is_account_locked(self):
        """Verificar si la cuenta está bloqueada por intentos fallidos"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_account(self, minutes=30):
        """Bloquear cuenta temporalmente"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.failed_login_attempts += 1
    
    def unlock_account(self):
        """Desbloquear cuenta"""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def record_login_attempt(self, success=True):
        """Registrar intento de login"""
        if success:
            self.last_login_at = datetime.utcnow()
            self.failed_login_attempts = 0
            self.locked_until = None
        else:
            self.failed_login_attempts += 1
            
            # Bloquear después de 5 intentos fallidos
            if self.failed_login_attempts >= 5:
                self.lock_account(30)  # 30 minutos
    
    def can_request_password_reset(self, cooldown_minutes=5):
        """Verificar si puede solicitar reset de contraseña"""
        if not self.last_password_reset_request:
            return True
        
        time_since_last = datetime.utcnow() - self.last_password_reset_request
        return time_since_last.total_seconds() > (cooldown_minutes * 60)
    
    def record_password_reset_request(self):
        """Registrar solicitud de reset de contraseña"""
        self.last_password_reset_request = datetime.utcnow()
    
    def get_full_name(self):
        """Obtener nombre completo"""
        return self.name
    
    def get_display_name(self):
        """Obtener nombre para mostrar"""
        return self.name or self.email.split('@')[0]
    
    def is_recently_created(self, hours=24):
        """Verificar si la cuenta fue creada recientemente"""
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.total_seconds() < (hours * 3600)
    
    def to_dict(self, include_sensitive=False):
        """Convertir a diccionario para API"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
        }
        
        if include_sensitive:
            data.update({
                'is_admin': self.is_admin,
                'is_premium': self.is_premium,
                'failed_login_attempts': self.failed_login_attempts,
                'is_locked': self.is_account_locked(),
                'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            })
        
        return data
    
    @classmethod
    def find_by_email(cls, email):
        """Buscar usuario por email"""
        return cls.query.filter_by(email=email.lower()).first()
    
    @classmethod
    def create_user(cls, name, email, password, **kwargs):
        """Crear nuevo usuario de forma segura"""
        user = cls(
            name=name,
            email=email.lower(),
            **kwargs
        )
        user.set_password(password)
        return user
    
    @classmethod
    def get_active_users(cls):
        """Obtener usuarios activos"""
        return cls.query.filter_by(is_active=True)
    
    @classmethod
    def get_verified_users(cls):
        """Obtener usuarios verificados"""
        return cls.query.filter_by(is_verified=True, is_active=True)
    
    @classmethod
    def cleanup_unverified_users(cls, days=7):
        """Limpiar usuarios no verificados después de X días"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        unverified_users = cls.query.filter(
            cls.is_verified == False,
            cls.created_at < cutoff_date
        ).all()
        
        count = len(unverified_users)
        
        for user in unverified_users:
            db.session.delete(user)
        
        db.session.commit()
        return count

    # Métodos requeridos por Flask-Login
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)


# Modelo opcional para trackear tokens de usuario
class UserToken(db.Model):
    """Modelo para trackear tokens activos de usuarios"""
    
    __tablename__ = 'user_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    jti = db.Column(db.String(255), nullable=False, unique=True, index=True)
    token_type = db.Column(db.String(50), nullable=False)  # 'api', 'refresh', etc.
    scopes = db.Column(db.Text)  # JSON string de scopes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_used_at = db.Column(db.DateTime)
    is_revoked = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<UserToken {self.jti}>'
    
    @classmethod
    def create_token_record(cls, user_id, jti, token_type, scopes, expires_at):
        """Crear registro de token"""
        import json
        
        token_record = cls(
            user_id=user_id,
            jti=jti,
            token_type=token_type,
            scopes=json.dumps(scopes) if scopes else None,
            expires_at=expires_at
        )
        
        db.session.add(token_record)
        return token_record
    
    @classmethod
    def revoke_token(cls, jti):
        """Revocar token específico"""
        token = cls.query.filter_by(jti=jti).first()
        if token:
            token.is_revoked = True
            return token
        return None
    
    @classmethod
    def cleanup_expired_tokens(cls):
        """Limpiar tokens expirados"""
        expired_count = cls.query.filter(
            cls.expires_at <= datetime.utcnow()
        ).delete()
        
        db.session.commit()
        return expired_count

from datetime import datetime
from app import db

class Operation(db.Model):
    __tablename__ = 'operations'

    # Tipos de eventos disponibles - fácil de expandir en el futuro
    EVENT_TYPES = {
        'login': 'Inicio de sesión',
        'update_profile': 'Actualización de perfil',
        'update_type_user': 'Cambio de tipo de usuario en el sistema',
        'logout': 'Cierre de sesión',
        'rest_password': 'Restablecimiento de contraseña',
        'crear_producto': 'Crear un producto',
        # Fácil agregar nuevos tipos aquí:
        # 'crear_negocio': 'Crear negocio TCP',
        # 'actualizar_negocio': 'Actualizar negocio TCP',
        # 'eliminar_cliente': 'Eliminar cliente/proveedor',
    }

    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con usuario
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Tipo de evento - validar contra EVENT_TYPES
    event_type = db.Column(db.String(50), nullable=False)
    
    # Descripción detallada del evento
    description = db.Column(db.Text, nullable=False)
    
    # Timestamp del evento
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relación con User
    user = db.relationship('User', backref=db.backref('operations', lazy=True, cascade='all, delete-orphan'))

    @classmethod
    def create_operation(cls, user_id, event_type, description=None):
        """
        Método helper para crear operaciones de forma consistente
        
        Args:
            user_id: ID del usuario
            event_type: Tipo de evento (debe estar en EVENT_TYPES)
            description: Descripción personalizada (opcional)
        """
        if event_type not in cls.EVENT_TYPES:
            raise ValueError(f"Tipo de evento '{event_type}' no válido. Tipos disponibles: {list(cls.EVENT_TYPES.keys())}")
        
        # Si no se proporciona descripción, usar la del diccionario
        if description is None:
            description = cls.EVENT_TYPES[event_type]
        
        operation = cls(
            user_id=user_id,
            event_type=event_type,
            description=description
        )
        
        db.session.add(operation)
        return operation

    @classmethod
    def log_user_activity(cls, user_id, event_type, custom_description=None):
        """
        Método conveniente para registrar actividad del usuario y hacer commit
        
        Args:
            user_id: ID del usuario
            event_type: Tipo de evento
            custom_description: Descripción personalizada (opcional)
        """
        try:
            operation = cls.create_operation(user_id, event_type, custom_description)
            db.session.commit()
            return operation
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_user_operations(cls, user_id, event_filter=None, limit=50):
        """
        Obtener operaciones de un usuario con filtros opcionales
        
        Args:
            user_id: ID del usuario
            event_filter: Filtrar por tipo de evento (opcional)
            limit: Límite de registros (default: 50)
        """
        query = cls.query.filter(cls.user_id == user_id)
        
        if event_filter and event_filter != 'all':
            query = query.filter(cls.event_type == event_filter)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()

    def get_event_display_name(self):
        """Obtener el nombre de visualización del evento"""
        return self.EVENT_TYPES.get(self.event_type, "Evento desconocido")

    def __repr__(self):
        return f'<Operation {self.event_type} by user {self.user_id} at {self.created_at}>'


# Función helper para usar en las rutas
def log_activity(user, event_type, description=None):
    """
    Función helper para registrar actividades desde las rutas
    
    Uso:
        log_activity(g.user, 'login')
        log_activity(g.user, 'crear_producto', 'Producto XYZ creado')
    """
    return Operation.log_user_activity(user.id, event_type, description)