import os
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user,login_required
from app.extensions import db
from app.utils.decorators import admin_required
from .forms import ComentarioForm, PublicacionForm
from werkzeug.utils import secure_filename
from app.models.blog  import  Comentario, Publicacion, PublicacionContenido

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/panel-admin')
@admin_required
def panel_admin():
    if not current_user.is_authenticated or not current_user.is_admin():
        flash('Acceso denegado. Debes ser administrador para acceder a esta sección.', 'danger')
        return redirect(url_for('main.home'))
    
    return render_template('admin/panel_admin.html')


@admin_bp.route('/blog')
def blog():
    publicaciones = Publicacion.query.order_by(Publicacion.fecha_creacion.desc()).all()
    return render_template('admin/lista.html', publicaciones=publicaciones)

@admin_bp.route('/crear', methods=['GET', 'POST'])
@admin_required
@login_required
def create_post():
    form = PublicacionForm()

    if form.validate_on_submit():
        titulo = form.title.data
        nueva = Publicacion(titulo=titulo, user_id=current_user.id)
        db.session.add(nueva)
        db.session.commit()  # Necesario para obtener nueva.id

        bloques = []
        i = 0
        contador = 1

        while True:
            tipo = request.form.get(f'bloques[{i}][tipo]')
            if not tipo:
                break

            if tipo == 'texto':
                contenido = request.form.get(f'bloques[{i}][contenido]')
                bloques.append({'tipo': 'texto', 'contenido': contenido})

            elif tipo == 'imagen':
                imagen = request.files.get(f'bloques[{i}][imagen]')
                if imagen and imagen.filename:
                    extension = os.path.splitext(imagen.filename)[1]
                    filename = f"foto_{current_user.id}_{nueva.id}_{contador}{extension}"

                    # Guardar en /static/uploads/
                    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                    ruta_absoluta = os.path.join(UPLOAD_FOLDER, filename)
                    imagen.save(ruta_absoluta)

                    # Ruta relativa sin 'static/'
                    ruta_relativa = f'uploads/{filename}'
                    bloques.append({'tipo': 'imagen', 'ruta': ruta_relativa})
                    contador += 1

            i += 1

        for idx, b in enumerate(bloques):
            bloque = PublicacionContenido(
                publicacion_id=nueva.id,
                tipo=b['tipo'],
                contenido=b.get('contenido'),
                ruta_imagen=b.get('ruta'),
                orden=idx
            )
            db.session.add(bloque)

        db.session.commit()
        flash("Publicación creada correctamente.", "success")
        return redirect(url_for('admin.ver_publicacion', id=nueva.id))

    return render_template('admin/create_post.html', form=form)


# Ruta para gestionar usuarios (cambiar roles, etc.)
@admin_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    # Aquí puedes pasar una lista de usuarios desde la base de datos
    return render_template('admin/manage_users.html')

@admin_bp.route('/<int:id>/comentar', methods=['POST'])
@login_required
def comentar(id):
    publicacion = Publicacion.query.get_or_404(id)
    form = ComentarioForm()

    if form.validate_on_submit():
        comentario = Comentario(
            publicacion_id=publicacion.id,
            user_id=current_user.id,
            contenido=form.contenido.data
        )
        db.session.add(comentario)
        db.session.commit()
        flash("Comentario enviado correctamente.", "success")
    else:
        flash("Error en el formulario. Revisa los campos.", "danger")

    return redirect(url_for('admin.ver_publicacion', id=id))

# Ruta para ver una publicación individual
@admin_bp.route('/<int:id>')
def ver_publicacion(id):
    publicacion = Publicacion.query.get_or_404(id)
    comentarios = Comentario.query.filter_by(publicacion_id=id).all()
    form = ComentarioForm()
    return render_template('admin/ver.html', publicacion=publicacion , comentarios=comentarios, form=form)