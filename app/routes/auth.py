from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.extensions import db, bcrypt
from app.utils.mail import enviar_correo_recuperacion, validar_token
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

        flash('Usuario creado exitosamente')
        return redirect(url_for('auth.login'))
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
    if current_user.is_authenticated:
        return redirect(url_for('main.inicio'))

    form = SolicitarRecuperacionForm()
    if form.validate_on_submit():
        usuario = User.query.filter_by(email=form.email.data).first()
        if usuario:
            enviar_correo_recuperacion(usuario)
        flash('Si el correo existe, se ha enviado un enlace para restablecer la contraseña.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/solicitar_recuperacion.html', form=form)

@auth_bp.route('/recuperar/<token>', methods=['GET', 'POST'])
def recuperar_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.inicio'))

    email = validar_token(token, salt='recuperar-password')
    if not email:
        flash('El enlace es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.solicitar_recuperacion'))

    usuario = User.query.filter_by(email=email).first()
    if not usuario:
        flash('Cuenta no encontrada.', 'warning')
        return redirect(url_for('auth.login'))

    form = RestablecerPasswordForm()
    if form.validate_on_submit():
        User.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Contraseña actualizada correctamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/restablecer_password.html', form=form)