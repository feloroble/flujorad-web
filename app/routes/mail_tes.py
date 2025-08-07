import logging
from flask import Blueprint, jsonify
from flask_mail import Message
from ..utils.mail import mail   # asegúrate de que esto esté bien importado

bp = Blueprint('test_mail', __name__)

@bp.route('/test-mail')
def test_send_mail():
    try:
        msg = Message(
            subject='📩 Prueba de correo - Tecno Táctil',
            recipients=['felix.roble@tecnotactil.com'],
            body='Este es un correo de prueba enviado desde la aplicación principal de Tecno Táctil.'
        )
        mail.send(msg)

        # Éxito
        logging.info("✅ Correo enviado correctamente desde la vista /test-mail")
        return jsonify({"success": True, "message": "Correo enviado correctamente"})

    except Exception as e:
        logging.error(f"❌ Error al enviar correo: {type(e).__name__}: {e}")
        # Mostrar error en pantalla (navegador o consola curl/postman)
        return jsonify({
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "hint": "Verifica conexión, puerto y credenciales SMTP en tus variables .env"
        }), 500