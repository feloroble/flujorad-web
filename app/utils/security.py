import jwt
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from flask import current_app
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64
import os

class TokenManager:
    """Manejo seguro de tokens para la aplicación"""
    
    @staticmethod
    def _get_secret_key() -> str:
        """Obtener clave secreta de la configuración"""
        return current_app.config.get('SECRET_KEY')
    
    @staticmethod
    def _get_salt() -> str:
        """Obtener salt adicional para mayor seguridad"""
        return current_app.config.get('SECURITY_SALT', 'default_salt_change_in_production')
    
    @staticmethod
    def generate_verification_token(email: str, expires_in: int = 86400) -> str:
        """
        Generar token de verificación de email seguro
        
        Args:
            email: Email del usuario
            expires_in: Tiempo de expiración en segundos (default: 24 horas)
            
        Returns:
            str: Token JWT seguro
        """
        try:
            payload = {
                'email': email,
                'purpose': 'email_verification',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'jti': secrets.token_hex(16),  # JWT ID único para prevenir replay attacks
                'salt': TokenManager._get_salt()
            }
            
            token = jwt.encode(
                payload,
                TokenManager._get_secret_key(),
                algorithm='HS256'
            )
            
            current_app.logger.info(f"Token de verificación generado para {email}")
            return token
            
        except Exception as e:
            current_app.logger.error(f"Error generando token de verificación: {str(e)}")
            return None
    
    @staticmethod
    def verify_verification_token(token: str) -> Optional[str]:
        """
        Verificar token de verificación de email
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            str: Email si el token es válido, None si no es válido
        """
        try:
            payload = jwt.decode(
                token,
                TokenManager._get_secret_key(),
                algorithms=['HS256']
            )
            
            # Verificar propósito del token
            if payload.get('purpose') != 'email_verification':
                current_app.logger.warning("Token con propósito incorrecto")
                return None
            
            # Verificar salt
            if payload.get('salt') != TokenManager._get_salt():
                current_app.logger.warning("Token con salt incorrecto")
                return None
            
            email = payload.get('email')
            current_app.logger.info(f"Token de verificación válido para {email}")
            return email
            
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token de verificación expirado")
            return None
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Token de verificación inválido: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error verificando token: {str(e)}")
            return None
    
    @staticmethod
    def generate_password_reset_token(email: str, user_id: int, expires_in: int = 3600) -> str:
        """
        Generar token de reset de contraseña ultra seguro
        
        Args:
            email: Email del usuario
            user_id: ID del usuario
            expires_in: Tiempo de expiración en segundos (default: 1 hora)
            
        Returns:
            str: Token JWT seguro
        """
        try:
            # Generar nonce único
            nonce = secrets.token_hex(32)
            
            payload = {
                'email': email,
                'user_id': user_id,
                'purpose': 'password_reset',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'jti': secrets.token_hex(16),
                'nonce': nonce,
                'salt': TokenManager._get_salt(),
                # Hash del timestamp para prevenir timing attacks
                'time_hash': hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
            }
            
            token = jwt.encode(
                payload,
                TokenManager._get_secret_key(),
                algorithm='HS256'
            )
            
            current_app.logger.info(f"Token de reset generado para usuario {user_id}")
            return token
            
        except Exception as e:
            current_app.logger.error(f"Error generando token de reset: {str(e)}")
            return None
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verificar token de reset de contraseña
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            dict: Datos del usuario si el token es válido, None si no es válido
        """
        try:
            payload = jwt.decode(
                token,
                TokenManager._get_secret_key(),
                algorithms=['HS256']
            )
            
            # Verificar propósito del token
            if payload.get('purpose') != 'password_reset':
                current_app.logger.warning("Token de reset con propósito incorrecto")
                return None
            
            # Verificar salt
            if payload.get('salt') != TokenManager._get_salt():
                current_app.logger.warning("Token de reset con salt incorrecto")
                return None
            
            result = {
                'email': payload.get('email'),
                'user_id': payload.get('user_id'),
                'jti': payload.get('jti')
            }
            
            current_app.logger.info(f"Token de reset válido para usuario {result['user_id']}")
            return result
            
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token de reset expirado")
            return None
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Token de reset inválido: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error verificando token de reset: {str(e)}")
            return None
    
    @staticmethod
    def generate_api_token(user_id: int, scopes: list = None, expires_in: int = 2592000) -> str:
        """
        Generar token de API para autenticación
        
        Args:
            user_id: ID del usuario
            scopes: Lista de permisos/scopes
            expires_in: Tiempo de expiración en segundos (default: 30 días)
            
        Returns:
            str: Token JWT para API
        """
        try:
            scopes = scopes or ['read']
            
            payload = {
                'user_id': user_id,
                'purpose': 'api_access',
                'scopes': scopes,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'jti': secrets.token_hex(16),
                'salt': TokenManager._get_salt()
            }
            
            token = jwt.encode(
                payload,
                TokenManager._get_secret_key(),
                algorithm='HS256'
            )
            
            current_app.logger.info(f"Token de API generado para usuario {user_id}")
            return token
            
        except Exception as e:
            current_app.logger.error(f"Error generando token de API: {str(e)}")
            return None
    
    @staticmethod
    def verify_api_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verificar token de API
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            dict: Datos del token si es válido, None si no es válido
        """
        try:
            payload = jwt.decode(
                token,
                TokenManager._get_secret_key(),
                algorithms=['HS256']
            )
            
            # Verificar propósito del token
            if payload.get('purpose') != 'api_access':
                return None
            
            # Verificar salt
            if payload.get('salt') != TokenManager._get_salt():
                return None
            
            return {
                'user_id': payload.get('user_id'),
                'scopes': payload.get('scopes', []),
                'jti': payload.get('jti')
            }
            
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token de API expirado")
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_secure_random_token(length: int = 32) -> str:
        """
        Generar token aleatorio criptográficamente seguro
        
        Args:
            length: Longitud del token en bytes
            
        Returns:
            str: Token hexadecimal seguro
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """
        Generar código OTP (One Time Password) numérico
        
        Args:
            length: Longitud del código
            
        Returns:
            str: Código OTP numérico
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        Generar hash seguro de un token para almacenamiento
        
        Args:
            token: Token a hashear
            
        Returns:
            str: Hash SHA-256 del token
        """
        return hashlib.sha256(
            (token + TokenManager._get_salt()).encode('utf-8')
        ).hexdigest()
    
    @staticmethod
    def verify_token_hash(token: str, token_hash: str) -> bool:
        """
        Verificar si un token coincide con su hash
        
        Args:
            token: Token original
            token_hash: Hash almacenado
            
        Returns:
            bool: True si coinciden, False si no
        """
        return secrets.compare_digest(
            TokenManager.hash_token(token),
            token_hash
        )


class TokenBlacklist:
    """Manejo de tokens invalidados/bloqueados"""
    
    @staticmethod
    def add_to_blacklist(jti: str, expires_at: datetime = None):
        """
        Agregar token a la lista negra
        
        Args:
            jti: JWT ID del token
            expires_at: Cuándo expira el token (para limpieza automática)
        """
        from app.models.token_blacklist import TokenBlacklistModel
        from app.extensions import db
        
        try:
            blacklist_entry = TokenBlacklistModel(
                jti=jti,
                blacklisted_at=datetime.utcnow(),
                expires_at=expires_at or datetime.utcnow() + timedelta(days=30)
            )
            
            db.session.add(blacklist_entry)
            db.session.commit()
            
            current_app.logger.info(f"Token {jti} agregado a lista negra")
            
        except Exception as e:
            current_app.logger.error(f"Error agregando token a lista negra: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def is_blacklisted(jti: str) -> bool:
        """
        Verificar si un token está en la lista negra
        
        Args:
            jti: JWT ID del token
            
        Returns:
            bool: True si está bloqueado, False si no
        """
        from app.models.token_blacklist import TokenBlacklistModel
        
        try:
            return TokenBlacklistModel.query.filter_by(jti=jti).first() is not None
        except Exception as e:
            current_app.logger.error(f"Error verificando lista negra: {str(e)}")
            return False
    
    @staticmethod
    def cleanup_expired_tokens():
        """Limpiar tokens expirados de la lista negra"""
        from app.models.token_blacklist import TokenBlacklistModel
        from app.extensions import db
        
        try:
            expired_tokens = TokenBlacklistModel.query.filter(
                TokenBlacklistModel.expires_at < datetime.utcnow()
            ).all()
            
            for token in expired_tokens:
                db.session.delete(token)
            
            db.session.commit()
            current_app.logger.info(f"Limpiados {len(expired_tokens)} tokens expirados")
            
        except Exception as e:
            current_app.logger.error(f"Error limpiando tokens expirados: {str(e)}")
            db.session.rollback()


# Funciones de conveniencia para mantener compatibilidad
def generate_verification_token(email: str) -> str:
    """Función de conveniencia para generar token de verificación"""
    return TokenManager.generate_verification_token(email)

def verify_verification_token(token: str) -> Optional[str]:
    """Función de conveniencia para verificar token de verificación"""
    return TokenManager.verify_verification_token(token)

def generate_reset_token(email: str, user_id: int) -> str:
    """Función de conveniencia para generar token de reset"""
    return TokenManager.generate_password_reset_token(email, user_id)

def verify_reset_token(token: str) -> Optional[Dict[str, Any]]:
    """Función de conveniencia para verificar token de reset"""
    return TokenManager.verify_password_reset_token(token)