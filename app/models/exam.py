from app.extensions.db import db
from datetime import datetime

class Exam(db.Model):
    __tablename__ = "exams"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados do exame
    exam_type = db.Column(db.String(50), nullable=False)  # Raio-X, Sangue, Urina, Foto, etc
    exam_name = db.Column(db.String(100))  # Nome específico
    file_path = db.Column(db.String(300))  # Caminho do arquivo
    file_name = db.Column(db.String(200))  # Nome original do arquivo
    file_size = db.Column(db.Integer)  # Tamanho em bytes
    results = db.Column(db.Text)  # Resultados textuais
    notes = db.Column(db.Text)  # Observações do médico

    # Análise da IA
    ai_analyzed = db.Column(db.Boolean, default=False)
    ai_analysis_date = db.Column(db.DateTime, nullable=True)
    ai_findings = db.Column(db.Text, nullable=True)  # Achados da IA
    ai_confidence = db.Column(db.Float, nullable=True)  # Confiança (0-100)
    ai_recommendations = db.Column(db.Text, nullable=True)  # Recomendações
    
    # Datas
    exam_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relações
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultations.id"), nullable=True)
    

    def __repr__(self):
        return f"<Exam {self.id} - {self.exam_type}>"