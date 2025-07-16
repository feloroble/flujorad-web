from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Configuración SMTP para puerto 465 y SSL
app.config['MAIL_SERVER'] = 'mail.privateemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'soporte@tecnotactil.com'
app.config['MAIL_PASSWORD'] = 'XgPivL1YW1PFOKQ4mPhLZcurWmT8yc'
app.config['MAIL_DEFAULT_SENDER'] = ('Tecno Táctil', 'soporte@tecnotactil.com')

mail = Mail(app)

with app.app_context():
    msg = Message(
        subject='Prueba de correo - Tecno Táctil',
        recipients=['roblefelix64@gmail.com'],
        body='Este es un correo de prueba enviado desde la aplicación Tecno Táctil.'
    )
    try:
        mail.send(msg)
        print('Correo enviado correctamente.')
    except Exception as e:
        print(f'Error al enviar correo: {e}')
