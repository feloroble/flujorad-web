from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
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

class BlogPostForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    content = TextAreaField('Contenido', validators=[DataRequired()])
    image = FileField('Imagen', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imágenes')])
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