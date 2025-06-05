import os
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user,login_required
from app.extensions import db
from app.utils.decorators import admin_required
from .forms import BlogPostForm
from werkzeug.utils import secure_filename
from app.models.blog  import BlogPost

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
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog_list.html', posts=posts)

@admin_bp.route('/crear', methods=['GET', 'POST'])
@admin_required
def create_post():
    if not current_user.is_admin:
        flash('No tienes permiso para crear publicaciones.')
        return redirect(url_for('main.home'))

    form = BlogPostForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads', image_filename)
            image_file.save(upload_path)

        post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            image_filename=image_filename,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Publicación creada con éxito.')
        return redirect(url_for('blog.index'))

    return render_template('admin/create_post.html', form=form)

# Ruta para gestionar usuarios (cambiar roles, etc.)
@admin_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    # Aquí puedes pasar una lista de usuarios desde la base de datos
    return render_template('admin/manage_users.html')

@admin_bp.route('/comments')
@admin_required
def comments():
    render_template('admin/post_comentario.html')