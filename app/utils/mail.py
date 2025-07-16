from flask_mail import Mail, Message
from flask import app, current_app, url_for, render_template
from itsdangerous import URLSafeTimedSerializer

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def generar_token(email, salt='confirmar-email'):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt=salt)

def validar_token(token, salt='confirmar-email', expira=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt=salt, max_age=expira)
    except Exception:
        return None

def enviar_correo_confirmacion(usuario):
    token = generar_token(usuario.email)
    link = url_for('auth.confirmar_email', token=token, _external=True)

    html = render_template('correo/confirmacion.html', usuario=usuario, link=link)
    text = f"Hola {usuario.nombre}, confirma tu cuenta accediendo al siguiente enlace: {link}"

    msg = Message('Confirma tu cuenta - Tecno Táctil', recipients=[usuario.email])
    msg.body = text
    msg.html = html
    mail.send(msg)

def enviar_correo_recuperacion(usuario):
    token = generar_token(usuario.email, salt='recuperar-password')
    link = url_for('auth.recuperar_password_token', token=token, _external=True)

    html = render_template('correo/recuperar_password.html', usuario=usuario, link=link)
    text = f"Hola {usuario.name}, restablece tu contraseña accediendo al siguiente enlace: {link}"

    msg = Message('Recupera tu contraseña - Tecno Táctil', recipients=[usuario.email])
    msg.body = text
    msg.html = html
    mail.send(msg)
