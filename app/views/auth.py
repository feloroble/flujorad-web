from flask import render_template,url_for
from . import auth_bp

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')


@auth_bp.route('/registro')
def registro():
    return render_template('auth/registro.html')