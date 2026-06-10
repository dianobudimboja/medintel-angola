from app.extensions.db import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    identification = db.Column(db.String(50), unique=True, nullable=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    contact = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relações
    histories = db.relationship("MedicalHistory", backref="patient", lazy=True)
    consultations = db.relationship("Consultation", backref="patient", lazy=True)
    exams = db.relationship("Exam", backref="patient", lazy=True)

    def __repr__(self):
        return f"<Patient {self.name}>"
