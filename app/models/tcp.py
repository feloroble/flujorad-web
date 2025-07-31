from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

class TCPBusiness(db.Model):
    __tablename__ = 'tcpbusiness'

    id = db.Column(db.Integer, primary_key=True)
    
    # Campos principales del negocio
    project_name = db.Column(db.String(255), nullable=False, comment="Nombre del proyecto TCP")
    description = db.Column(db.Text, nullable=False, comment="Descripción del proyecto")
    main_activity = db.Column(db.String(255), nullable=False, comment="Actividad principal")

    # Campos de información adicional
    is_registered_in_conservation_zone = db.Column(db.Boolean, nullable=False, comment="Registrado en las Zonas Priorizadas para la Conservación")
    has_bank_account = db.Column(db.Boolean, nullable=False, comment="Posee cuenta bancaria")
    payment_method = db.Column(db.String(10), nullable=False, comment="Método de pago")  # Validar: Tarjeta, Efectivo
    bank_type = db.Column(db.String(20), nullable=True, comment="Tipo de banco")  # Validar: Metropolitano, BANDEC, BPA
    fiscal_bank_branch = db.Column(db.String(255), nullable=True, comment="Sucursal bancaria de su domicilio fiscal")
    has_transportation = db.Column(db.Boolean, nullable=False, comment="Posee un medio de transporte")
    does_ecommerce = db.Column(db.Boolean, nullable=False, comment="Realiza comercio electrónico")

    # Detalles adicionales
    location = db.Column(db.String(255), nullable=False, comment="Lugar donde ejerce")
    residential_commercial_area = db.Column(db.Boolean, nullable=False, comment="Área comercial en vivienda")
    music_service = db.Column(db.Boolean, nullable=False, comment="Servicio de música")
    operation_hours = db.Column(db.String(255), nullable=False, comment="Horario de funcionamiento de la instalación")
    nic = db.Column(db.String(50), nullable=False, comment="NIC")
    business_address = db.Column(db.Text, nullable=False, comment="Dirección del negocio")
    
    contact_phone = db.Column(db.String(15), nullable=True, comment="Teléfono de contacto")
    contact_email = db.Column(db.String(100), nullable=True, comment="Correo de contacto")

    # Relación con usuario
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Campos de control
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="Fecha de creación")

    # Relaciones
    user = db.relationship('User', backref=db.backref('tcp_businesses', lazy=True, cascade='all, delete-orphan'))
    relations = db.relationship('BusinessRelation', foreign_keys='BusinessRelation.business_id', backref='business', lazy=True, cascade='all, delete-orphan')
    related_as = db.relationship('BusinessRelation', foreign_keys='BusinessRelation.related_business_id', backref='related_business', lazy=True)
    tariffs = db.relationship('ServiceTariff', backref='business', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TCPBusiness {self.project_name}>'


class BusinessRelation(db.Model):
    __tablename__ = 'business_relation'

    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones
    business_id = db.Column(db.Integer, db.ForeignKey('tcpbusiness.id', ondelete='CASCADE'), nullable=False)
    related_business_id = db.Column(db.Integer, db.ForeignKey('tcpbusiness.id', ondelete='SET NULL'), nullable=True)
    
    # Para clientes/proveedores nuevos no registrados en TCPBusiness
    name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Define si es cliente o proveedor
    type = db.Column(db.String(10), nullable=False)  # Validar: Cliente, Proveedor
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BusinessRelation {self.type}: {self.name or self.related_business_id}>'


class ServiceTariff(db.Model):
    __tablename__ = 'servicetariff'

    id = db.Column(db.Integer, primary_key=True)
    
    business_id = db.Column(db.Integer, db.ForeignKey('tcpbusiness.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    end_date = db.Column(db.Date, nullable=True)  # Null si no hay fin definido o es indefinido

    def __repr__(self):
        return f'<ServiceTariff {self.price} for business {self.business_id}>'