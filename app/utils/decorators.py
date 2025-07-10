
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from functools import wraps

from app.utils.activos import MODULOS_ACTIVOS

# Decorador para rutas que requieren rol de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acceso restringido a administradores.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

