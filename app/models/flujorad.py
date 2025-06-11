from datetime import datetime
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