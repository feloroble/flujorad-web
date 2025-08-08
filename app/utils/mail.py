from flask import current_app, render_template
from flask_mail import Mail, Message
import logging
import os
import smtplib
import socket
from typing import List, Optional, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Instancia global de Flask-Mail
mail = Mail()

class EmailService:
    """Servicio para manejo de correos electrónicos optimizado para Ionos"""
    
    @staticmethod
    def _validate_ionos_config():
        """Validar configuración específica de Ionos"""
        required_configs = [
            'MAIL_SERVER',
            'MAIL_PORT', 
            'MAIL_USERNAME',
            'MAIL_PASSWORD',
            'MAIL_USE_TLS'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not current_app.config.get(config):
                missing_configs.append(config)
        
        if missing_configs:
            current_app.logger.error(f"Configuraciones faltantes para Ionos: {', '.join(missing_configs)}")
            return False
            
        # Validar que el servidor sea de Ionos
        server = current_app.config.get('MAIL_SERVER', '').lower()
        if not any(ionos_domain in server for ionos_domain in ['ionos.it', 'ionos.com', 'ionos.es', 'ionos.de']):
            current_app.logger.warning(f"Servidor SMTP no parece ser de Ionos: {server}")
        
        return True
    
    @staticmethod
    def _test_ionos_connection():
        """Probar conectividad específica con Ionos"""
        try:
            server = current_app.config.get('MAIL_SERVER')
            port = current_app.config.get('MAIL_PORT', 587)
            
            # Test conectividad básica
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((server, port))
            sock.close()
            
            if result != 0:
                current_app.logger.error(f"No se puede conectar a {server}:{port}")
                return False
            
            # Test handshake SMTP
            smtp_server = smtplib.SMTP(server, port)
            smtp_server.set_debuglevel(0)
            smtp_server.ehlo()
            
            if current_app.config.get('MAIL_USE_TLS'):
                smtp_server.starttls()
            
            # Test login
            smtp_server.login(
                current_app.config.get('MAIL_USERNAME'),
                current_app.config.get('MAIL_PASSWORD')
            )
            
            smtp_server.quit()
            current_app.logger.info("Conexión con Ionos SMTP exitosa")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error conectando con Ionos: {str(e)}")
            return False
    
    @staticmethod
    def send_email(
        subject: str,
        recipients: Union[str, List[str]],
        template: str,
        template_vars: dict = None,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[dict] = None,
        sender: str = None,
        retry_count: int = 3
    ) -> dict:
        """
        Enviar correo electrónico usando plantillas HTML optimizado para Ionos
        
        Args:
            subject: Asunto del correo
            recipients: Lista de destinatarios o string con un solo destinatario
            template: Nombre del template HTML (sin extensión)
            template_vars: Variables para el template
            cc: Lista de destinatarios en copia
            bcc: Lista de destinatarios en copia oculta
            attachments: Lista de archivos adjuntos
            sender: Remitente (opcional, usa el por defecto si no se especifica)
            retry_count: Número de reintentos en caso de fallo
            
        Returns:
            dict: Resultado con success, error_message, etc.
        """
        
        # Validar configuración de Ionos
        if not EmailService._validate_ionos_config():
            return {
                "success": False,
                "error_message": "Configuración de Ionos incompleta",
                "error_type": "ConfigurationError",
                "hint": "Verifica variables de entorno MAIL_* para Ionos"
            }
        
        try:
            # Validar parámetros
            if not recipients:
                current_app.logger.error("No se especificaron destinatarios")
                return {
                    "success": False,
                    "error_message": "No se especificaron destinatarios",
                    "error_type": "ValidationError"
                }
                
            if isinstance(recipients, str):
                recipients = [recipients]
            
            # Variables por defecto para templates
            if template_vars is None:
                template_vars = {}
                
            # Agregar variables globales del contexto
            template_vars.update({
                'app_name': current_app.config.get('APP_NAME', 'Tecno Táctil'),
                'app_version': current_app.config.get('APP_VERSION', '1.0.0'),
                'base_url': current_app.config.get('BASE_URL', 'http://localhost:5000'),
                'company_name': current_app.config.get('COMPANY_NAME', 'Tecno Táctil'),
                'support_email': current_app.config.get('SUPPORT_EMAIL', current_app.config.get('MAIL_USERNAME'))
            })
            
            # Renderizar template HTML
            try:
                html_body = render_template(f'emails/{template}.html', **template_vars)
            except Exception as e:
                current_app.logger.error(f"Error al renderizar template {template}: {str(e)}")
                return {
                    "success": False,
                    "error_message": f"Error al renderizar template {template}",
                    "error_type": "TemplateError",
                    "hint": f"Verifica que existe el archivo templates/emails/{template}.html"
                }
            
            # Intentar renderizar versión texto plano (opcional)
            text_body = None
            try:
                text_body = render_template(f'emails/{template}.txt', **template_vars)
            except:
                # Si no existe versión texto, generar una básica
                import re
                # Remover tags HTML básicos para versión texto
                text_body = re.sub('<[^<]+?>', '', html_body)
                text_body = f"{text_body}\n\n---\nEnviado desde {current_app.config.get('APP_NAME', 'Tecno Táctil')}"
            
            # Intentar envío con reintentos
            last_error = None
            for attempt in range(retry_count):
                try:
                    # Crear mensaje
                    msg = Message(
                        subject=subject,
                        recipients=recipients,
                        html=html_body,
                        body=text_body,
                        cc=cc,
                        bcc=bcc,
                        sender=sender or current_app.config.get('MAIL_USERNAME')
                    )
                    
                    # Configurar headers adicionales para Ionos
                    msg.extra_headers = {
                        'X-Mailer': f"{current_app.config.get('APP_NAME', 'TecnoTactil')} via Ionos",
                        'X-Priority': '3',
                        'Importance': 'Normal'
                    }
                    
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
                    
                    current_app.logger.info(
                        f"✅ Correo enviado exitosamente via Ionos a {', '.join(recipients)} "
                        f"(intento {attempt + 1}/{retry_count})"
                    )
                    
                    return {
                        "success": True,
                        "message": "Email enviado correctamente",
                        "recipients": recipients,
                        "attempts": attempt + 1
                    }
                    
                except Exception as e:
                    last_error = e
                    current_app.logger.warning(
                        f"⚠️ Intento {attempt + 1}/{retry_count} fallido: {str(e)}"
                    )
                    
                    # Si no es el último intento, esperar un poco
                    if attempt < retry_count - 1:
                        import time
                        time.sleep(2 ** attempt)  # Backoff exponencial
            
            # Si llegamos aquí, todos los intentos fallaron
            error_msg = str(last_error) if last_error else "Error desconocido"
            current_app.logger.error(f"❌ Error al enviar correo después de {retry_count} intentos: {error_msg}")
            
            # Clasificar tipo de error
            error_type = "SMTPError"
            hint = "Verifica conexión, puerto y credenciales SMTP en tus variables .env"
            
            if "Authentication" in error_msg or "Login" in error_msg:
                error_type = "AuthenticationError"
                hint = "Verifica usuario y contraseña de Ionos"
            elif "Connection" in error_msg or "timeout" in error_msg:
                error_type = "ConnectionError"
                hint = "Verifica conectividad con smtp.ionos.it:587"
            elif "Permission denied" in error_msg:
                error_type = "PermissionError"
                hint = "Puerto SMTP bloqueado. Contacta soporte de Ionos para desbloquear"
            
            return {
                "success": False,
                "error_message": error_msg,
                "error_type": error_type,
                "hint": hint,
                "attempts": retry_count
            }
            
        except Exception as e:
            current_app.logger.error(f"❌ Error crítico al enviar correo: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "error_type": "CriticalError",
                "hint": "Error crítico en el servicio de email"
            }
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str, verification_token: str = None) -> dict:
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
    def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> dict:
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
    def send_contact_notification(name: str, email: str, subject: str, message: str) -> dict:
        """Enviar notificación de contacto al administrador"""
        admin_email = current_app.config.get('ADMIN_EMAIL', current_app.config.get('MAIL_USERNAME'))
        
        if not admin_email:
            current_app.logger.error("No se ha configurado email de administrador")
            return {
                "success": False,
                "error_message": "Email de administrador no configurado",
                "error_type": "ConfigurationError"
            }
            
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
    def send_order_confirmation(user_email: str, user_name: str, order_data: dict) -> dict:
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
    def test_email_configuration() -> dict:
        """Probar la configuración de correo con Ionos"""
        try:
            # Primero validar configuración
            if not EmailService._validate_ionos_config():
                return {
                    "success": False,
                    "error_message": "Configuración incompleta",
                    "error_type": "ConfigurationError"
                }
            
            # Test de conectividad
            if not EmailService._test_ionos_connection():
                return {
                    "success": False,
                    "error_message": "No se puede conectar a Ionos SMTP",
                    "error_type": "ConnectionError"
                }
            
            # Test de envío real
            admin_email = current_app.config.get('MAIL_USERNAME')
            if not admin_email:
                return {
                    "success": False,
                    "error_message": "MAIL_USERNAME no configurado",
                    "error_type": "ConfigurationError"
                }
                
            result = EmailService.send_email(
                subject="✅ Prueba de configuración Ionos - Tecno Táctil",
                recipients=admin_email,
                template="test_email",
                template_vars={
                    'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'server': current_app.config.get('MAIL_SERVER'),
                    'port': current_app.config.get('MAIL_PORT')
                }
            )
            
            if result['success']:
                current_app.logger.info("✅ Test de configuración Ionos exitoso")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"❌ Error en prueba de correo Ionos: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "error_type": "TestError"
            }
    
    @staticmethod 
    def get_ionos_status() -> dict:
        """Obtener estado de la configuración de Ionos"""
        config_status = {
            'MAIL_SERVER': bool(current_app.config.get('MAIL_SERVER')),
            'MAIL_PORT': bool(current_app.config.get('MAIL_PORT')),
            'MAIL_USERNAME': bool(current_app.config.get('MAIL_USERNAME')),
            'MAIL_PASSWORD': bool(current_app.config.get('MAIL_PASSWORD')),
            'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS', False)
        }
        
        server = current_app.config.get('MAIL_SERVER', '').lower()
        is_ionos = any(domain in server for domain in ['ionos.it', 'ionos.com', 'ionos.es', 'ionos.de'])
        
        return {
            'configured': all(config_status.values()),
            'is_ionos_server': is_ionos,
            'server': current_app.config.get('MAIL_SERVER'),
            'port': current_app.config.get('MAIL_PORT'),
            'username': current_app.config.get('MAIL_USERNAME'),
            'tls_enabled': current_app.config.get('MAIL_USE_TLS'),
            'config_details': config_status
        }


# Funciones de conveniencia para mantener compatibilidad
def send_email(subject, recipients, template, **template_vars):
    """Función de conveniencia para envío básico"""
    result = EmailService.send_email(subject, recipients, template, template_vars)
    return result['success']  # Mantener compatibilidad con return bool

def send_welcome_email(user_email, user_name, verification_token=None):
    """Función de conveniencia para correo de bienvenida"""
    result = EmailService.send_welcome_email(user_email, user_name, verification_token)
    return result['success']

def send_password_reset_email(user_email, user_name, reset_token):
    """Función de conveniencia para reset de contraseña"""
    result = EmailService.send_password_reset_email(user_email, user_name, reset_token)
    return result['success']


# Comandos CLI actualizados para Ionos
def init_mail_commands(app):
    """Inicializar comandos CLI para correo con Ionos"""
    
    @app.cli.command("test-ionos")
    def test_ionos_cmd():
        """Probar configuración de Ionos"""
        result = EmailService.test_email_configuration()
        if result['success']:
            print("✅ Configuración de Ionos funcionando correctamente")
        else:
            print(f"❌ Error en configuración: {result.get('error_message')}")
            print(f"💡 Sugerencia: {result.get('hint', 'Revisar configuración')}")
    
    @app.cli.command("ionos-status")
    def ionos_status_cmd():
        """Ver estado de configuración de Ionos"""
        status = EmailService.get_ionos_status()
        
        print("📧 Estado de configuración Ionos:")
        print(f"  Servidor: {status['server']}")
        print(f"  Puerto: {status['port']}")
        print(f"  Usuario: {status['username']}")
        print(f"  TLS: {'✅' if status['tls_enabled'] else '❌'}")
        print(f"  Es servidor Ionos: {'✅' if status['is_ionos_server'] else '❌'}")
        print(f"  Configuración completa: {'✅' if status['configured'] else '❌'}")
        
        if not status['configured']:
            print("\n⚠️ Configuraciones faltantes:")
            for key, value in status['config_details'].items():
                if not value:
                    print(f"  - {key}")
            
    @app.cli.command("send-test-ionos")
    @click.argument('recipient')
    def send_test_ionos_cmd(recipient):
        """Enviar correo de prueba a un destinatario específico via Ionos"""
        result = EmailService.send_email(
            subject="🚀 Correo de prueba desde Ionos CLI",
            recipients=recipient,
            template="test_email",
            template_vars={
                'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'server': current_app.config.get('MAIL_SERVER'),
                'via': 'Comando CLI'
            }
        )
        
        if result['success']:
            print(f"✅ Correo enviado exitosamente a {recipient} via Ionos")
            print(f"📊 Intentos utilizados: {result.get('attempts', 1)}")
        else:
            print(f"❌ Error enviando a {recipient}: {result.get('error_message')}")
            print(f"💡 Sugerencia: {result.get('hint', 'Revisar logs')}")

# Imports necesarios para los comandos CLI
try:
    import click
    from datetime import datetime
except ImportError:
    # Los comandos CLI son opcionales
    pass