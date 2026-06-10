from app.extensions.db import db
from datetime import datetime

class MedicalHistory(db.Model):
    __tablename__ = "medical_histories"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados do histórico
    condition = db.Column(db.String(200))  # Doença / Condição
    notes = db.Column(db.Text)  # Notas clínicas
    treatment = db.Column(db.Text)  # Tratamento realizado
    
    # Datas
    diagnosis_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relações
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultations.id"), nullable=True)
    
    
    
    def __repr__(self):
        return f"<MedicalHistory {self.id} - {self.condition}>"