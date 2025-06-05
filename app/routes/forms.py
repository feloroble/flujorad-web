from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

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