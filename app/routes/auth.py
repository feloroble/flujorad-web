import email
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from ..utils.tokens import confirm_reset_token, generate_reset_token

from ..utils.mail import EmailService, send_email
from ..models.user import User
from ..extensions import db, bcrypt

from .forms import LoginForm, RegisterForm, RestablecerPasswordForm, SolicitarRecuperacionForm
from werkzeug.security import generate_password_hash



auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Credenciales inválidas')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
       form = RegisterForm()
       if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este correo ya está registrado')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()

        if EmailService.send_welcome_email(
            user_email=user.email,
            user_name=user.name
            
        ):
            flash('Registro exitoso. Revisa tu correo para verificar tu cuenta.', 'success')
        else:
            flash('Registro exitoso, pero hubo un problema enviando el correo de confirmación.', 'warning')
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash('Error en el registro. Inténtalo de nuevo.', 'error')
        return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/terminos')
def terminos():
    return render_template('auth/terminos.html')

@auth_bp.route('/recuperar', methods=['GET', 'POST'])
def solicitar_recuperacion():

    form = SolicitarRecuperacionForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            # Enviar correo de recuperación
            if EmailService.send_password_reset_email(
               user_email=user.email,
               user_name=user.name,
               reset_token=token
            ):
            
               flash('Se ha enviado un enlace de recuperación a tu correo.', 'info')
            else:
               flash('Error al enviar el correo. Inténtalo más tarde.', 'error')
        else:
           flash('Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/solicitar_recuperacion.html', form=form)

@auth_bp.route('/recuperar/<token>', methods=['GET', 'POST'])
def recuperar_password_token(token):
    email = confirm_reset_token(token)
    if not email:
        flash('El enlace es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.solicitar_recuperacion'))

    form = RestablecerPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.commit()
            flash('Tu contraseña ha sido actualizada.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/restablecer_password.html', form=form)