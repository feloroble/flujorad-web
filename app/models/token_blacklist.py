from datetime import datetime
from ..extensions import db
from models.base import BaseModel

class TokenBlacklistModel(BaseModel):
    """Modelo para tokens invalidados/bloqueados"""
    
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), nullable=False, unique=True, index=True)
    blacklisted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(100), default='manual_revocation')
    
    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'
    
    @classmethod
    def is_jti_blacklisted(cls, jti: str) -> bool:
        """Verificar si un JTI está en la lista negra"""
        return cls.query.filter_by(jti=jti).first() is not None
    
    @classmethod
    def add_jti_to_blacklist(cls, jti: str, expires_at: datetime = None, reason: str = 'manual_revocation'):
        """Agregar JTI a la lista negra"""
        if not expires_at:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=30)
        
        blacklist_entry = cls(
            jti=jti,
            expires_at=expires_at,
            reason=reason
        )
        
        db.session.add(blacklist_entry)
        return blacklist_entry
    
    @classmethod
    def cleanup_expired(cls):
        """Limpiar tokens expirados"""
        expired_count = cls.query.filter(
            cls.expires_at <= datetime.utcnow()
        ).delete()
        
        db.session.commit()
        return expired_count