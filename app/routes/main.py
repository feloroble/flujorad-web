from flask import Blueprint, render_template

main_bp = Blueprint('main',  __name__)

@main_bp.route('/')
def home():

    return render_template('index.html')

@main_bp.route('/contacto')
def contacto():
    return render_template('contacto.html')

@main_bp.route('/acerca-de')
def acerca_de():
    return render_template('acerca_de.html')
