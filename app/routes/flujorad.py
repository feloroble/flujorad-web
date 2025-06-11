

from app.extensions import db
from flask_login import login_required
from app.utils.decorators import admin_required
from flask import Blueprint, redirect, render_template, request, url_for

from app.models.flujorad import LoadModel, Standard
from app.routes.forms import StandardForm


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
    form = LoadModel()
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

