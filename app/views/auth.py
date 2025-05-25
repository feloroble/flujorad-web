from flask import render_template,url_for
from . import auth_bp
from app.database import db

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')


@auth_bp.route('/registro')
def registro():
    return render_template('auth/registro.html')

@auth_bp.route('/check_db')
def check_db():
      try:
        # Consulta de prueba (ej: listar tablas en MariaDB)
        tables = db.execute_sql("SHOW TABLES;").fetchall()
        return {"status": "¡Conexión exitosa!", "tables": tables}
      except Exception as e:
        return {"status": "Error de conexión", "error": str(e)}, 500