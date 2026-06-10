from app.extensions.db import db
from datetime import datetime

class Consultation(db.Model):
    __tablename__ = "consultations"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados da consulta
    symptoms = db.Column(db.Text, nullable=False)  # Sintomas atuais
    vital_signs = db.Column(db.String(200))  # Sinais vitais: pressão, temperatura, etc
    observations = db.Column(db.Text)  # Observações do médico
    notes = db.Column(db.Text)  # Notas adicionais
    
    # Status
    status = db.Column(db.String(20), default="em_andamento")  # em_andamento, concluida
    
    # Datas
    consultation_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relações
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relação com diagnóstico (um para um)
    diagnosis = db.relationship("Diagnosis", backref="consultation", uselist=False)
    
    def __repr__(self):
        return f"<Consultation {self.id} - Patient {self.patient_id}>"