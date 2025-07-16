from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length,EqualTo
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2)])
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Crear cuenta')

class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    subject = StringField('Asunto', validators=[DataRequired()])
    message = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Enviar mensaje')

class PublicacionForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    submit = SubmitField('Publicar')

class ModelForm(FlaskForm):
    name = StringField('Nombre del Modelo', validators=[DataRequired(), Length(max=100)])
    parameter_a = FloatField('Parámetro A', validators=[DataRequired()])
    parameter_b = FloatField('Parámetro B', validators=[DataRequired()])
    submit = SubmitField('Guardar Modelo')


class StandardForm(FlaskForm):
    name = StringField('Nombre de la Norma', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Guardar Norma')


class GeneralDataForm(FlaskForm):
    circuit_name = StringField('Nombre del Circuito', validators=[DataRequired(), Length(max=150)])
    base_power = FloatField('Potencia Base', validators=[DataRequired()])
    base_voltage = FloatField('Tensión Base del Nodo 0', validators=[DataRequired()])
    specific_voltage = FloatField('Tensión Específica para Nodo 0', validators=[DataRequired()])
    standard_id = SelectField('Norma', coerce=int, validators=[DataRequired()])
    model_id = SelectField('Modelo', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Datos')

class NodoDataForm(FlaskForm):
    nombre_nodo = StringField('Nombre del Nodo', validators=[DataRequired(), Length(max=100)])
    carga_real = FloatField('Carga Real (P)', validators=[DataRequired()])
    carga_imaginaria = FloatField('Carga Imaginaria (Q)', validators=[DataRequired()])
    valor_condensador = FloatField('Valor del Condensador (kvar)', validators=[])
    tension_base_nodo = FloatField('Tensión Base del Nodo', validators=[DataRequired()])
    submit = SubmitField('Guardar Nodo')


class ComentarioForm(FlaskForm):
    contenido = TextAreaField('Comentario', validators=[DataRequired()])
    submit = SubmitField('Comentar')


class SolicitarRecuperacionForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar enlace de recuperación')

class RestablecerPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirmar', message='Las contraseñas deben coincidir')
    ])
    confirmar = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    submit = SubmitField('Restablecer contraseña')