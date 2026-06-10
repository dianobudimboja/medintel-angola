from app.models.medical_history import MedicalHistory
from app.models.consultation import Consultation
from app.models.diagnosis import Diagnosis
from app.models.exam import Exam
from app.extensions.db import db
from datetime import datetime

def add_to_medical_history(patient_id, condition, notes, treatment, consultation_id=None):
    """Adicionar entrada ao histórico clínico"""
    
    history = MedicalHistory(
        patient_id=patient_id,
        condition=condition,
        notes=notes,
        treatment=treatment,
        consultation_id=consultation_id,
        diagnosis_date=datetime.now()
    )
    
    db.session.add(history)
    db.session.commit()
    return history

def get_patient_history(patient_id):
    """Buscar histórico completo do paciente"""
    
    # Histórico manual
    history_entries = MedicalHistory.query.filter_by(patient_id=patient_id).order_by(
        MedicalHistory.diagnosis_date.desc()
    ).all()
    
    # Consultas com diagnósticos
    consultations = Consultation.query.filter_by(patient_id=patient_id).order_by(
        Consultation.consultation_date.desc()
    ).all()
    
    # Exames
    exams = Exam.query.filter_by(patient_id=patient_id).order_by(
        Exam.exam_date.desc()
    ).all()
    
    return {
        'history_entries': history_entries,
        'consultations': consultations,
        'exams': exams
    }

def generate_clinical_summary(patient_id):
    """Gerar resumo clínico do paciente para IA"""
    
    history = get_patient_history(patient_id)
    
    summary = {
        'patient_id': patient_id,
        'total_consultations': len(history['consultations']),
        'total_exams': len(history['exams']),
        'diagnoses': [],
        'medications': [],
        'chronic_conditions': []
    }
    
    # Extrair diagnósticos
    for consultation in history['consultations']:
        if consultation.diagnosis:
            summary['diagnoses'].append({
                'date': consultation.consultation_date.isoformat(),
                'diagnosis': consultation.diagnosis.doctor_diagnosis,
                'notes': consultation.diagnosis.doctor_notes
            })
    
    # Extrair condições crónicas do histórico manual
    for entry in history['history_entries']:
        summary['chronic_conditions'].append({
            'id': entry.id,
            'date': entry.diagnosis_date.isoformat(),
            'condition': entry.condition,
            'treatment': entry.treatment,
            'notes': entry.notes
        })
    
    return summary