from datetime import datetime
from app.extensions import db
from flask_login import UserMixin



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' o 'user'
    profile_picture = db.Column(db.String(255), nullable=True)  # Ruta a la imagen

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_admin(self):
        return self.role == 'admin'

    def is_user(self):
        return self.role == 'user'

    def __repr__(self):
        return f'<User {self.email}>'

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