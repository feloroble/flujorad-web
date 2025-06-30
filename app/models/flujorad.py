from datetime import datetime
import math
from app.extensions import db




class Standard(db.Model):
    __tablename__ = 'standards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Ej: 'ANSI C48.1', 'NUEVA NORMA'

    def __repr__(self):
        return f'<Standard {self.name}>'
    

class LoadModel(db.Model):
    __tablename__ = 'load_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Ej: 'S Constante', 'I Constante', etc.

    parametro_a = db.Column(db.Float, nullable=True)
    parametro_b = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<LoadModel {self.name}>'
    

class GeneralData(db.Model):
    __tablename__ = 'general_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    circuit_name = db.Column(db.String(100), nullable=False)
    base_power = db.Column(db.Float, nullable=False)
    base_voltage_n0 = db.Column(db.Float, nullable=False)
    specific_voltage_n0 = db.Column(db.Float, nullable=True)

    standard_id = db.Column(db.Integer, db.ForeignKey('standards.id'), nullable=True)
    model_id = db.Column(db.Integer, db.ForeignKey('load_models.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('general_data', lazy=True))
    standard = db.relationship('Standard', backref=db.backref('general_data', lazy=True))
    model = db.relationship('LoadModel', backref=db.backref('general_data', lazy=True))

    def __repr__(self):
        return f'<GeneralData {self.circuit_name}>'
class Circuito(db.Model):
    __tablename__ = 'circuitos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    general_data_id = db.Column(db.Integer, db.ForeignKey('general_data.id'), nullable=False)  # referencia dato general base
    nodo_base_id = db.Column(db.Integer, db.ForeignKey('nodo_data.id'), nullable=False)  # nodo base

    nombre = db.Column(db.String(100), nullable=False)

    general_data = db.relationship('GeneralData', backref='circuitos')
    nodo_base = db.relationship('NodoData', foreign_keys=[nodo_base_id])

    
class NodoData(db.Model):
    __tablename__ = 'nodo_data'

    id = db.Column(db.Integer, primary_key=True)
    circuito_id = db.Column(db.Integer, db.ForeignKey('circuitos.id'), nullable=False)
    nombre_nodo = db.Column(db.String(100), nullable=False)
    carga_real = db.Column(db.Float, nullable=False)         # P
    carga_imaginaria = db.Column(db.Float, nullable=False)   # Q original
    valor_condensador = db.Column(db.Float, nullable=True)   # Qc (en kvar)
    tension_base_nodo = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    circuito = db.relationship('Circuito', backref='nodos', foreign_keys=[circuito_id])

    @property
    def fp_sin_condensador(self):
        """Factor de potencia sin condensador."""
        p = self.carga_real
        q = self.carga_imaginaria
        return round(p / math.sqrt(p**2 + q**2), 4) if p != 0 else 0.0

    @property
    def fp_con_condensador(self):
        """Factor de potencia con condensador aplicado (Q - Qc)."""
        p = self.carga_real
        q = self.carga_imaginaria
        qc = self.valor_condensador or 0.0
        q_compensada = q - qc
        return round(p / math.sqrt(p**2 + q_compensada**2), 4) if p != 0 else 0.0

    def __repr__(self):
        return f"<NodoData Nodo={self.nombre_nodo} Carga=({self.carga_real}+{self.carga_imaginaria}j)>"
    
class Linea(db.Model):
    __tablename__ = 'lineas'

    id = db.Column(db.Integer, primary_key=True)
    circuito_id = db.Column(db.Integer, db.ForeignKey('circuitos.id'), nullable=False)
    nodo_envio_id = db.Column(db.Integer, db.ForeignKey('nodo_data.id'), nullable=False)
    nodo_recepcion_id = db.Column(db.Integer, db.ForeignKey('nodo_data.id'), nullable=False)

    nombre_nodo_envio = db.Column(db.String(100), nullable=False)
    nombre_nodo_recepcion = db.Column(db.String(100), nullable=False)

    numero_circuitos = db.Column(db.Integer, nullable=False)

    tipo = db.Column(db.Enum('linea', 'transformador', name='tipo_linea'), nullable=False)

    # Solo para líneas
    resistencia = db.Column(db.Float, nullable=True)
    reactancia = db.Column(db.Float, nullable=True)
    susceptancia = db.Column(db.Float, nullable=True)

    # Solo para transformadores
    relacion_transformacion = db.Column(db.Float, nullable=True)  # V1/V2
    impedancia_resistencia = db.Column(db.Float, nullable=True)
    impedancia_reactancia = db.Column(db.Float, nullable=True)
    admitancia_magnetizacion = db.Column(db.Float, nullable=True)
    potencia_nominal = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    circuito = db.relationship('Circuito', backref='lineas')
    nodo_envio = db.relationship('NodoData', foreign_keys=[nodo_envio_id], backref=db.backref('lineas_envio', lazy=True))
    nodo_recepcion = db.relationship('NodoData', foreign_keys=[nodo_recepcion_id], backref=db.backref('lineas_recepcion', lazy=True))

    def __repr__(self):
        return f'<Linea {self.nombre_nodo_envio} → {self.nombre_nodo_recepcion}>'
    
class Resultado(db.Model):
    __tablename__ = 'resultados'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    general_data_id = db.Column(db.Integer, db.ForeignKey('general_data.id'), nullable=False)
    nodo_base_id = db.Column(db.Integer, db.ForeignKey('nodo_data.id'), nullable=False)
    circuito_id = db.Column(db.Integer, db.ForeignKey('circuitos.id'), nullable=False)

    resultados_json = db.Column(db.Text, nullable=False)  # Ejemplo de almacenamiento resultados
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    general_data = db.relationship('GeneralData')
    nodo_base = db.relationship('NodoData')
    circuito = db.relationship('Circuito')