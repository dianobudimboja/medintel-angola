from app.models.consultation import Consultation
from app.models.diagnosis import Diagnosis
from app.models.exam import Exam
from app.extensions.db import db
from datetime import datetime
import json

# ============ CONSULTAS ============

def create_consultation(patient_id, doctor_id, symptoms, vital_signs=None, observations=None):
    """Criar nova consulta"""
    consultation = Consultation(
        patient_id=patient_id,
        doctor_id=doctor_id,
        symptoms=symptoms,
        vital_signs=vital_signs,
        observations=observations,
        status="em_andamento"
    )
    db.session.add(consultation)
    db.session.commit()
    return consultation

def get_consultation_by_id(consultation_id):
    """Buscar consulta por ID"""
    return Consultation.query.get(consultation_id)

def get_patient_consultations(patient_id):
    """Buscar todas consultas de um paciente (ordenadas por data)"""
    return Consultation.query.filter_by(patient_id=patient_id).order_by(Consultation.consultation_date.desc()).all()

def get_recent_consultations(doctor_id=None, limit=10):
    """Buscar consultas recentes"""
    query = Consultation.query.order_by(Consultation.consultation_date.desc())
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    return query.limit(limit).all()

def update_consultation(consultation_id, symptoms=None, vital_signs=None, observations=None):
    """Atualizar consulta"""
    consultation = get_consultation_by_id(consultation_id)
    if consultation:
        if symptoms:
            consultation.symptoms = symptoms
        if vital_signs:
            consultation.vital_signs = vital_signs
        if observations:
            consultation.observations = observations
        consultation.updated_at = datetime.utcnow()
        db.session.commit()
    return consultation

def close_consultation(consultation_id):
    """Finalizar consulta"""
    consultation = get_consultation_by_id(consultation_id)
    if consultation:
        consultation.status = "concluida"
        consultation.updated_at = datetime.utcnow()
        db.session.commit()
    return consultation

# ============ DIAGNÓSTICOS ============

def create_diagnosis(consultation_id, doctor_diagnosis, ai_suggestion=None, 
                     ai_confidence=None, doctor_notes=None, 
                     prescribed_medication=None, recommendations=None,
                     follow_up_date=None):
    """Criar diagnóstico para uma consulta"""
    diagnosis = Diagnosis(
        consultation_id=consultation_id,
        doctor_diagnosis=doctor_diagnosis,
        ai_suggestion=json.dumps(ai_suggestion) if ai_suggestion else None,
        ai_confidence=ai_confidence,
        ai_analysis_date=datetime.utcnow() if ai_suggestion else None,
        doctor_notes=doctor_notes,
        prescribed_medication=prescribed_medication,
        recommendations=recommendations,
        follow_up_date=follow_up_date,
        status="ativo"
    )
    db.session.add(diagnosis)
    db.session.commit()
    
    # Fechar a consulta
    close_consultation(consultation_id)
    
    return diagnosis

def get_diagnosis_by_consultation(consultation_id):
    """Buscar diagnóstico por consulta"""
    return Diagnosis.query.filter_by(consultation_id=consultation_id).first()

def update_diagnosis(diagnosis_id, **kwargs):
    """Atualizar diagnóstico"""
    diagnosis = Diagnosis.query.get(diagnosis_id)
    if diagnosis:
        for key, value in kwargs.items():
            if hasattr(diagnosis, key):
                setattr(diagnosis, key, value)
        diagnosis.updated_at = datetime.utcnow()
        db.session.commit()
    return diagnosis

# ============ EXAMES ============

def add_exam(patient_id, exam_type, exam_name=None, file_path=None, results=None, 
             notes=None, consultation_id=None):
    """Adicionar exame"""
    exam = Exam(
        patient_id=patient_id,
        exam_type=exam_type,
        exam_name=exam_name,
        file_path=file_path,
        results=results,
        notes=notes,
        consultation_id=consultation_id
    )
    db.session.add(exam)
    db.session.commit()
    return exam

def get_patient_exams(patient_id):
    """Buscar todos exames de um paciente"""
    return Exam.query.filter_by(patient_id=patient_id).order_by(Exam.exam_date.desc()).all()

def get_exam_by_id(exam_id):
    """Buscar exame por ID"""
    return Exam.query.get(exam_id)

# ============ IA (SIMULADA POR ENQUANTO) ============

def simulate_ai_analysis(symptoms, patient_history=None):
    """Simular análise da IA (substituir por modelo real depois)"""
    import random
    
    # Doenças comuns em Angola
    diseases = {
        "Malária": ["febre", "dor de cabeça", "calafrios", "suor"],
        "Febre Tifoide": ["febre alta", "dor abdominal", "dor de cabeça", "falta de apetite"],
        "Tuberculose": ["tosse persistente", "febre", "suor noturno", "perda de peso"],
        "Gripe": ["febre", "tosse", "dor de garganta", "congestão nasal"],
        "Dengue": ["febre alta", "dor atrás dos olhos", "dores musculares", "manchas vermelhas"]
    }
    
    # Contar correspondências
    symptom_list = symptoms.lower().split()
    probabilities = {}
    
    for disease, keywords in diseases.items():
        matches = sum(1 for keyword in keywords if keyword in symptom_list or keyword in symptoms.lower())
        probability = (matches / len(keywords)) * 100
        if probability > 0:
            probabilities[disease] = round(probability, 1)
    
    # Ordenar por probabilidade
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    
    # Simular alertas
    alerts = []
    if "Malária" in probabilities and probabilities["Malária"] > 50:
        alerts.append("⚠️ Risco elevado de Malária - considerar teste rápido")
    if "febre alta" in symptoms.lower() and "manchas" in symptoms.lower():
        alerts.append("⚠️ Possível Dengue - monitorizar sinais de alarme")
    
    return {
        "possibilidades": [{"doenca": d, "probabilidade": p} for d, p in sorted_probs[:3]],
        "alertas": alerts,
        "exames_sugeridos": ["Hemograma", "Teste rápido de Malária"] if "Malária" in probabilities else ["Avaliação clínica"]
    }