from app.extensions.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Campos existentes
    specialty = db.Column(db.String(50), nullable=True)
    hospital = db.Column(db.String(100), nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NOVOS CAMPOS PARA ADMIN
    role = db.Column(db.String(20), default='medico')  # super_admin, admin, medico
    is_active = db.Column(db.Boolean, default=True)  # Conta ativa/inativa
    is_verified = db.Column(db.Boolean, default=False)  # Verificação de credenciais
    verification_document = db.Column(db.String(200), nullable=True)  # Documento de verificação
    verification_notes = db.Column(db.Text, nullable=True)  # Notas sobre verificação
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Quem verificou
    verified_at = db.Column(db.DateTime, nullable=True)  # Data da verificação
    verification_requested_at = db.Column(db.DateTime, nullable=True)  # Data do pedido de verificação
    
    # Status da verificação: pending, approved, rejected, none
    verification_status = db.Column(db.String(20), default='none')  # none, pending, approved, rejected
    
    # Documentos de verificação
    license_number = db.Column(db.String(50), nullable=True)  # Nº da cédula profissional
    document_path = db.Column(db.String(200), nullable=True)  # Caminho do documento
    
    # Relações
    consultations = db.relationship("Consultation", backref="doctor", lazy=True)
    verified_by_user = db.relationship("User", remote_side=[id], foreign_keys=[verified_by])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def is_admin(self):
        return self.role in ['super_admin', 'admin']
    
    def is_verified_doctor(self):
        return self.is_verified and self.is_active
    
    @property
    def password(self):
        raise AttributeError('Password não é um atributo legível')
    
    @password.setter
    def password(self, password):
        self.set_password(password)
    
    def __repr__(self):
        return f"<User {self.name} ({self.role})>"