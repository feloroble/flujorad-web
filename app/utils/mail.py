from flask import current_app, render_template
from flask_mail import Mail, Message
import logging
import os
from typing import List, Optional, Union

# Instancia global de Flask-Mail
mail = Mail()

class EmailService:
    """Servicio para manejo de correos electrónicos"""
    
    @staticmethod
    def send_email(
        subject: str,
        recipients: Union[str, List[str]],
        template: str,
        template_vars: dict = None,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[dict] = None,
        sender: str = None
    ) -> bool:
        """
        Enviar correo electrónico usando plantillas HTML
        
        Args:
            subject: Asunto del correo
            recipients: Lista de destinatarios o string con un solo destinatario
            template: Nombre del template HTML (sin extensión)
            template_vars: Variables para el template
            cc: Lista de destinatarios en copia
            bcc: Lista de destinatarios en copia oculta
            attachments: Lista de archivos adjuntos
            sender: Remitente (opcional, usa el por defecto si no se especifica)
            
        Returns:
            bool: True si se envió correctamente, False en caso de error
        """
        
        try:
            # Validar parámetros
            if not recipients:
                current_app.logger.error("No se especificaron destinatarios")
                return False
                
            if isinstance(recipients, str):
                recipients = [recipients]
            
            # Variables por defecto para templates
            if template_vars is None:
                template_vars = {}
                
            # Agregar variables globales del contexto
            template_vars.update({
                'app_name': current_app.config.get('APP_NAME', 'Tecno Táctil'),
                'app_version': current_app.config.get('APP_VERSION', '1.0.0'),
                'base_url': current_app.config.get('BASE_URL', 'http://localhost:5000')
            })
            
            # Renderizar template HTML
            try:
                html_body = render_template(f'emails/{template}.html', **template_vars)
            except Exception as e:
                current_app.logger.error(f"Error al renderizar template {template}: {str(e)}")
                return False
            
            # Intentar renderizar versión texto plano (opcional)
            text_body = None
            try:
                text_body = render_template(f'emails/{template}.txt', **template_vars)
            except:
                # Si no existe versión texto, generar una básica
                text_body = f"Este correo requiere un cliente que soporte HTML.\n\n{current_app.config.get('APP_NAME', 'Tecno Táctil')}"
            
            # Crear mensaje
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                body=text_body,
                cc=cc,
                bcc=bcc,
                sender=sender
            )
            
            # Agregar archivos adjuntos si los hay
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, dict):
                        msg.attach(
                            attachment.get('filename', 'attachment'),
                            attachment.get('content_type', 'application/octet-stream'),
                            attachment.get('data')
                        )
            
            # Enviar correo
            mail.send(msg)
            
            current_app.logger.info(f"Correo enviado exitosamente a {', '.join(recipients)}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error al enviar correo: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str, verification_token: str = None) -> bool:
        """Enviar correo de bienvenida"""
        return EmailService.send_email(
            subject="¡Bienvenido a Tecno Táctil!",
            recipients=user_email,
            template="welcome",
            template_vars={
                'user_name': user_name,
                'verification_token': verification_token,
                'verification_url': f"{current_app.config.get('BASE_URL', '')}/verify/{verification_token}" if verification_token else None
            }
        )
    
    @staticmethod
    def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> bool:
        """Enviar correo de recuperación de contraseña"""
        return EmailService.send_email(
            subject="Recuperación de contraseña - Tecno Táctil",
            recipients=user_email,
            template="password_reset",
            template_vars={
                'user_name': user_name,
                'reset_token': reset_token,
                'reset_url': f"{current_app.config.get('BASE_URL', '')}/reset-password/{reset_token}",
                'expiry_time': current_app.config.get('TOKEN_EXPIRATION', 3600) // 60  # minutos
            }
        )
    
    @staticmethod
    def send_contact_notification(name: str, email: str, subject: str, message: str) -> bool:
        """Enviar notificación de contacto al administrador"""
        admin_email = current_app.config.get('ADMIN_EMAIL', current_app.config.get('MAIL_USERNAME'))
        
        if not admin_email:
            current_app.logger.error("No se ha configurado email de administrador")
            return False
            
        return EmailService.send_email(
            subject=f"Nuevo mensaje de contacto: {subject}",
            recipients=admin_email,
            template="contact_notification",
            template_vars={
                'contact_name': name,
                'contact_email': email,
                'contact_subject': subject,
                'contact_message': message
            }
        )
    
    @staticmethod
    def send_order_confirmation(user_email: str, user_name: str, order_data: dict) -> bool:
        """Enviar confirmación de pedido"""
        return EmailService.send_email(
            subject=f"Confirmación de pedido #{order_data.get('order_id')} - Tecno Táctil",
            recipients=user_email,
            template="order_confirmation",
            template_vars={
                'user_name': user_name,
                'order': order_data
            }
        )
    
    @staticmethod
    def test_email_configuration() -> bool:
        """Probar la configuración de correo"""
        try:
            admin_email = current_app.config.get('MAIL_USERNAME')
            if not admin_email:
                current_app.logger.error("MAIL_USERNAME no configurado")
                return False
                
            return EmailService.send_email(
                subject="Prueba de configuración de correo",
                recipients=admin_email,
                template="test_email",
                template_vars={
                    'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        except Exception as e:
            current_app.logger.error(f"Error en prueba de correo: {str(e)}")
            return False


# Funciones de conveniencia para mantener compatibilidad
def send_email(subject, recipients, template, **template_vars):
    """Función de conveniencia para envío básico"""
    return EmailService.send_email(subject, recipients, template, template_vars)

def send_welcome_email(user_email, user_name, verification_token=None):
    """Función de conveniencia para correo de bienvenida"""
    return EmailService.send_welcome_email(user_email, user_name, verification_token)

def send_password_reset_email(user_email, user_name, reset_token):
    """Función de conveniencia para reset de contraseña"""
    return EmailService.send_password_reset_email(user_email, user_name, reset_token)


# Comando CLI para probar correo (opcional)
def init_mail_commands(app):
    """Inicializar comandos CLI para correo"""
    
    @app.cli.command("test-email")
    def test_email_cmd():
        """Probar configuración de correo"""
        if EmailService.test_email_configuration():
            print("✅ Correo de prueba enviado correctamente")
        else:
            print("❌ Error al enviar correo de prueba")
            
    @app.cli.command("send-test-email")
    @click.argument('recipient')
    def send_test_email_cmd(recipient):
        """Enviar correo de prueba a un destinatario específico"""
        if EmailService.send_email(
            subject="Correo de prueba desde CLI",
            recipients=recipient,
            template="test_email",
            template_vars={'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ):
            print(f"✅ Correo de prueba enviado a {recipient}")
        else:
            print(f"❌ Error al enviar correo a {recipient}")

# Imports necesarios para los comandos CLI
try:
    import click
    from datetime import datetime
except ImportError:
    # Los comandos CLI son opcionales
    pass