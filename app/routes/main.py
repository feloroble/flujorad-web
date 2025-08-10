from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from ..extensions import db
from app.models.contact_message import ContactMessage
from ..utils.mail import EmailService

from .forms  import ContactForm

main_bp = Blueprint('main',  __name__)

@main_bp.route('/')
def home():

    return render_template('index.html')

@main_bp.route('/terminos-y-condiciones')
def terminos():
    return render_template('publico/terminos.html')
@main_bp.route('/politica-de-privacidad')
def politica():
    return render_template('publico/privasidad.html')    

@main_bp.route('/contacto', methods=['GET', 'POST'])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            name = current_user.name
            email = current_user.email
            subject = form.subject.data
            message = form.message.data

            msg = ContactMessage(
                user_id=current_user.id,
                name=name,
                email=email,
                subject=subject,
                message=message
            )
        else:
            name = form.name.data
            email = form.email.data
            subject = form.subject.data
            message = form.message.data

            msg = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
        
        db.session.add(msg)
        db.session.commit()

        if EmailService.send_contact_notification(
            name=name,
            email=email,
            subject=subject,
            message=message
        ):
            flash('Tu mensaje ha sido enviado correctamente. Te contactaremos pronto.', 'success')
        else:
            flash('Error al enviar tu mensaje. Por favor inténtalo más tarde.', 'error')

        return redirect(url_for('main.contacto'))

    return render_template('contacto.html', form=form)

@main_bp.route('/marketing-digital')
def marketing_digital():
    return render_template('publico/servicio_1.html')

@main_bp.route('/pagina-web')
def pagina_web():
    return render_template('publico/servicio_2.html')

@main_bp.route('/tienda-online')
def tienda_online():
    return render_template('publico/servicio_3.html')

@main_bp.route('/automatizacion')
def automatizacion():
    return render_template('publico/servicio_4.html')

@main_bp.route('/pos-ventas')
def pos_ventas():
    return render_template('publico/servicio_5.html')

@main_bp.route('/mantenimiento')
def mantenimiento():
    return render_template('publico/servicio_6.html')
