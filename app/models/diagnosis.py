from app.extensions.db import db
from datetime import datetime

class Diagnosis(db.Model):
    __tablename__ = "diagnoses"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # IA
    ai_suggestion = db.Column(db.Text)  # Sugestão da IA (JSON com probabilidades)
    ai_confidence = db.Column(db.Float)  # Confiança da IA (0-100)
    ai_analysis_date = db.Column(db.DateTime)  # Quando a IA analisou
    
    # Médico
    doctor_diagnosis = db.Column(db.String(200), nullable=False)  # Diagnóstico final do médico
    doctor_notes = db.Column(db.Text)  # Notas do médico
    
    # Tratamento
    prescribed_medication = db.Column(db.Text)  # Medicamentos prescritos
    recommendations = db.Column(db.Text)  # Recomendações adicionais
    
    # Follow-up
    follow_up_date = db.Column(db.DateTime)  # Próxima consulta
    treatment_outcome = db.Column(db.String(50))  # Resultado do tratamento
    
    # Status
    status = db.Column(db.String(20), default="ativo")  # ativo, concluido, arquivado
    
    # Datas
    diagnosis_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relações
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultations.id"), nullable=False)
    
    def __repr__(self):
        return f"<Diagnosis {self.id} - {self.doctor_diagnosis}>"