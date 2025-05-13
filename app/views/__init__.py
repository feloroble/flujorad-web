from flask import Blueprint

main_bp = Blueprint('main', __name__)
from app.views import main

auth_bp = Blueprint('auth', __name__)
from app.views import auth

