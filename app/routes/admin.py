import os
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user,login_required
from ..extensions import db
from ..utils.decorators import admin_required
from ..models.user import User
from .forms import ComentarioForm, DeletePostForm, PublicacionForm
from werkzeug.utils import secure_filename
from ..models.blog  import  Comentario, Publicacion, PublicacionContenido
from flask_wtf.csrf import validate_csrf, CSRFError

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


@admin_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    if current_user.role != 'admin':
        abort(403)

    try:
        # ===== VALIDAR TOKEN CSRF =====
        validate_csrf(request.form.get('csrf_token'))
        
        post = Publicacion.query.get_or_404(post_id)
        
        # Verificar que el post_id del formulario coincida con la URL
        form_post_id = request.form.get('post_id', type=int)
        if form_post_id != post_id:
            flash('Datos del formulario no válidos.', 'danger')
            return redirect(url_for('admin.posts_list'))
        
        db.session.delete(post)
        db.session.commit()
        flash('Publicación eliminada correctamente.', 'success')
        
    except CSRFError:
        flash('Token de seguridad inválido. Intenta nuevamente.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la publicación.', 'danger')
        # Log del error para debugging
        current_app.logger.error(f'Error eliminando publicación {post_id}: {str(e)}')
    
    return redirect(url_for('admin.posts_list'))

@admin_bp.route('/posts/delete', methods=['GET', 'POST'])
@login_required
def delete_posts_view():
    if current_user.role != 'admin':
        abort(403)

    # Crear formulario para eliminación
    delete_form = DeletePostForm()

    # Filtrar
    filtro_titulo = request.args.get('titulo', '', type=str)
    filtro_usuario = request.args.get('usuario', '', type=str)

    query = Publicacion.query

    if filtro_titulo:
        query = query.filter(Publicacion.titulo.ilike(f'%{filtro_titulo}%'))
    if filtro_usuario:
        query = query.join(Publicacion.usuario).filter(User.username.ilike(f'%{filtro_usuario}%'))

    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = query.order_by(Publicacion.fecha_creacion.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    publicaciones = pagination.items

    if request.method == 'POST':
        # ===== VALIDAR FORMULARIO CON CSRF =====
        if delete_form.validate_on_submit():
            post_id = delete_form.post_id.data
            post = Publicacion.query.get_or_404(post_id)
            
            try:
                comentarios = Comentario.query.filter_by(publicacion_id=post_id).all()
                for comentario in comentarios:
                  db.session.delete(comentario)
                db.session.delete(post)
                db.session.commit()
                flash('Publicación eliminada correctamente.', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash('Error al eliminar la publicación.', 'danger')
                current_app.logger.error(f'Error eliminando publicación {post_id}: {str(e)}')
            
            # Redirigir manteniendo los filtros
            return redirect(url_for('admin.delete_posts_view', 
                                  titulo=filtro_titulo, 
                                  usuario=filtro_usuario, 
                                  page=page))
        else:
            # Manejar errores de validación (incluyendo CSRF)
            if delete_form.errors:
                flash('Token de seguridad inválido. Intenta nuevamente.', 'danger')

    return render_template('admin/delete_posts.html', 
                         publicaciones=publicaciones, 
                         pagination=pagination,
                         filtro_titulo=filtro_titulo, 
                         filtro_usuario=filtro_usuario,
                         delete_form=delete_form)