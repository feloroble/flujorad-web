

from app.extensions import db
from flask_login import current_user, login_required
from app.utils.decorators import admin_required
from flask import Blueprint, abort, redirect, render_template, request, url_for, flash

from app.models.flujorad import Circuito, GeneralData, Linea, LoadModel, NodoData, Standard
from app.routes.forms import GeneralDataForm, ModelForm, NodoDataForm, StandardForm

flujorad_bp = Blueprint('flujorad', __name__)

@flujorad_bp.route('/standards', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_standards():
    form = StandardForm()
    if form.validate_on_submit():
        new_standard = Standard(name=form.name.data)
        db.session.add(new_standard)
        db.session.commit()
        return redirect(url_for('flujorad.manage_standards'))

    standards = Standard.query.all()
    return render_template('flujorad/standard_form.html', form=form, standards=standards)

@flujorad_bp.route('/load-models', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_load_models():
    form = ModelForm()
    if form.validate_on_submit():
        model = LoadModel(
            name=form.name.data,
            parametro_a=form.parameter_a.data,
            parametro_b=form.parameter_b.data
        )
        db.session.add(model)
        db.session.commit()
        return redirect(url_for('flujorad.manage_load_models'))

    models = LoadModel.query.all()
    return render_template('flujorad/model_form.html', form=form, models=models)

@flujorad_bp.route('/datos_generales/<int:general_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_datos_generales(general_id):
    general = GeneralData.query.get_or_404(general_id)
    if general.user_id != current_user.id:
        abort(403)
    form = GeneralDataForm(obj=general)
    if form.validate_on_submit():
        form.populate_obj(general)
        db.session.commit()
        flash('Datos generales actualizados.', 'success')
        return redirect(url_for('flujorad.ver_circuitos'))
    return render_template('flujorad/editar_datos_generales.html', form=form)

@flujorad_bp.route('/circuito/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_circuito():
    # Aquí implementa la lógica para crear un nuevo circuito, según tu modelo Circuito
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if not nombre:
            flash('El nombre es obligatorio.', 'danger')
            return redirect(url_for('flujorad.nuevo_circuito'))
        nuevo = Circuito(nombre=nombre, user_id=current_user.id)
        db.session.add(nuevo)
        db.session.commit()
        flash('Circuito creado correctamente.', 'success')
        return redirect(url_for('flujorad.ver_circuitos'))
    return render_template('flujorad/nuevo_circuito.html')

@flujorad_bp.route('/circuito/<int:circuito_id>/eliminar', methods=['POST'])
@login_required
def eliminar_circuito(circuito_id):
    circuito = Circuito.query.get_or_404(circuito_id)
    if circuito.user_id != current_user.id:
        abort(403)
    db.session.delete(circuito)
    db.session.commit()
    flash('Circuito eliminado.', 'success')
    return redirect(url_for('flujorad.ver_circuitos'))

@flujorad_bp.route('/iniciar_flujo', methods=['POST'])
@login_required
def iniciar_flujo():
    general_id = request.form.get('general_id')
    circuito_id = request.form.get('circuito_id')

    # Validar existencia y permisos
    general = GeneralData.query.filter_by(id=general_id, user_id=current_user.id).first()
    circuito = Circuito.query.filter_by(id=circuito_id, user_id=current_user.id).first()

    if not general or not circuito:
        flash('Selección inválida.', 'danger')
        return redirect(url_for('flujorad.ver_circuitos'))

    # Aquí ejecuta el cálculo o redirige a la vista de resultados
    # Por ejemplo, redirigir a una vista para mostrar resultados del flujo
    flash('Cálculo de flujo iniciado.', 'info')
    return redirect(url_for('flujorad.resultado_flujo', general_id=general.id, circuito_id=circuito.id))

@flujorad_bp.route('/resultado_flujo/<int:general_id>/<int:circuito_id>')
@login_required
def resultado_flujo(general_id, circuito_id):
    # Verifica permisos
    general = GeneralData.query.filter_by(id=general_id, user_id=current_user.id).first_or_404()
    circuito = Circuito.query.filter_by(id=circuito_id, user_id=current_user.id).first_or_404()

    # Implementa lógica para mostrar resultados de flujo de carga
    # Por ahora solo muestra plantilla placeholder
    return render_template('flujorad/resultado_flujo.html', general=general, circuito=circuito)