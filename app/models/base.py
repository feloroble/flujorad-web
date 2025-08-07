from datetime import datetime
from app import db

class BaseModel(db.Model):
    """Modelo base con campos comunes y métodos útiles"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Guardar instancia"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar: {e}")
            return False
    
    def delete(self):
        """Eliminar instancia"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar: {e}")
            return False
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}