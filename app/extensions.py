from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()


def casmbio_base_impedancia(Z_dada,PB_dada,PB_nueva,VB_nueva,VB_dada):
    """
    Calculo de cambio de base de impedancias o admitancias.

    Parámetros:
    Z_dada (float): Impedancia dada en ohmios.
    PB_dada (float): Potencia base dada en MVA.
    VB_dada (float): Voltaje base dado en kV.
    PB_nueva (float): Nueva potencia base en MVA.
    VB_nueva (float): Nuevo voltaje base en kV.

    Retorna:
    float: Impedancia base en ohmios.
    """
    return Z_dada * (PB_nueva/PB_dada) / (VB_dada * VB_nueva)**2

    salida = str(casmbio_base_impedancia(float(Z_dada), float(PB_dada), float(PB_nueva), float(VB_nueva), float(25)))

    Z_dada = str(Z_dada)
