from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from app.extensions import db
from app.models.flujorad import Circuito, GeneralData

user_bp = Blueprint('user', __name__)

@user_bp.route('/panel-user')
def panel_user():
    datos_generales = GeneralData.query.filter_by(user_id=current_user.id).all()
    circuitos = Circuito.query.filter_by(id=current_user.id).all()
    return render_template('user/panel_user.html',
        datos_generales=datos_generales,
        circuitos=circuitos
    )

@user_bp.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    if request.method == 'POST':
        if current_user.is_authenticated:
            current_user.name = request.form.get('name', current_user.name)
            current_user.email = request.form.get('email', current_user.email)
            db.session.commit()
            flash('Perfil actualizado correctamente.', 'success')
        else:
            flash('Debes iniciar sesión para editar tu perfil.', 'danger')
        return redirect(url_for('user.panel_user'))

    return render_template('user/editar_perfil.html', user=current_user)