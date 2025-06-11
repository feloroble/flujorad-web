

from app.extensions import db
from flask_login import current_user, login_required
from app.utils.decorators import admin_required
from flask import Blueprint, redirect, render_template, request, url_for,flash

from app.models.flujorad import GeneralData, LoadModel, Standard
from app.routes.forms import GeneralDataForm, ModelForm, StandardForm


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

@flujorad_bp.route('/general-data', methods=['GET', 'POST'])
@login_required
def create_general_data():
    form = GeneralDataForm()

    # Llenado dinámico de opciones
    form.standard_id.choices = [(s.id, s.name) for s in Standard.query.all()]
    form.model_id.choices = [(m.id, m.name) for m in LoadModel.query.all()]

    if form.validate_on_submit():
        data = GeneralData(
            user_id=current_user.id,
            circuit_name=form.circuit_name.data,
            base_power=form.base_power.data,
            base_voltage_n0=form.base_voltage.data,
            specific_voltage_n0=form.specific_voltage.data,
            standard_id=form.standard_id.data,
            model_id=form.model_id.data
        )
        db.session.add(data)
        db.session.commit()
        flash('Datos generales guardados correctamente.', 'success')
        return redirect(url_for('admin.panel_admin'))

    return render_template('flujorad/general_data_form.html', form=form)
