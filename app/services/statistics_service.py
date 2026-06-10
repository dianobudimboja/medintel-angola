from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.exam import Exam
from app.models.diagnosis import Diagnosis
from datetime import datetime, timedelta
from flask_login import current_user
from datetime import timedelta

def get_dashboard_stats(doctor_id=None):
    """Buscar estatísticas para o dashboard"""
    
    # Pacientes totais
    total_patients = Patient.query.count()
    
    # Consultas de hoje
    today = datetime.now().date()
    today_start = datetime(today.year, today.month, today.day, 0, 0, 0)
    today_end = datetime(today.year, today.month, today.day, 23, 59, 59)
    
    query = Consultation.query.filter(
        Consultation.consultation_date >= today_start,
        Consultation.consultation_date <= today_end
    )
    
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    
    today_consultations = query.count()
    
    # Exames pendentes (sem resultados)
    thirty_days_ago = datetime.now() - timedelta(days=30)

    pending_exams = Exam.query.filter(
        (Exam.results == None) | (Exam.results == ''),
        Exam.created_at >= thirty_days_ago
    ).count()
    
    # Análises IA Hoje - contar exames analisados pela IA hoje
    ai_analyses_today = Exam.query.filter(
        Exam.ai_analyzed == True,
        Exam.ai_analysis_date >= today_start,
        Exam.ai_analysis_date <= today_end
    ).count()
    
    # Se não houver exames analisados hoje, contar também diagnósticos com IA
    if ai_analyses_today == 0:
        ai_analyses_today = Diagnosis.query.filter(
            Diagnosis.ai_suggestion != None,
            Diagnosis.ai_suggestion != '',
            Diagnosis.created_at >= today_start,
            Diagnosis.created_at <= today_end
        ).count()
    
    return {
        'total_patients': total_patients,
        'today_consultations': today_consultations,
        'pending_exams': pending_exams,
        'ai_analyses_today': ai_analyses_today
    }


def get_recent_patients(doctor_id=None, limit=5):
    """Buscar pacientes recentes"""
    query = Consultation.query.order_by(Consultation.consultation_date.desc())
    
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    
    recent_consultations = query.limit(limit).all()
    
    recent_patients = []
    for consultation in recent_consultations:
        if consultation.patient:
            recent_patients.append({
                'id': consultation.patient.id,
                'name': consultation.patient.name,
                'age': consultation.patient.age,
                'gender': consultation.patient.gender,
                'last_consultation': consultation.consultation_date,
                'diagnosis': consultation.diagnosis.doctor_diagnosis if consultation.diagnosis else 'Pendente'
            })
    
    return recent_patients

def get_disease_statistics():
    """Estatísticas de doenças mais comuns (baseado em diagnósticos reais)"""
    from sqlalchemy import func
    
    # Buscar diagnósticos reais do sistema
    diseases = Diagnosis.query.with_entities(
        Diagnosis.doctor_diagnosis, 
        func.count(Diagnosis.id).label('total')
    ).group_by(Diagnosis.doctor_diagnosis).order_by(func.count(Diagnosis.id).desc()).limit(5).all()
    
    total = sum(d[1] for d in diseases) if diseases else 100
    
    if diseases and total > 0:
        result = []
        for disease, count in diseases:
            percentage = round((count / total) * 100)
            result.append({
                'name': disease,
                'count': count,
                'percentage': percentage
            })
        return result
    else:
        # Dados de exemplo
        return [
            {'name': 'Malária', 'count': 0, 'percentage': 45},
            {'name': 'Febre Tifoide', 'count': 0, 'percentage': 20},
            {'name': 'Tuberculose', 'count': 0, 'percentage': 15},
            {'name': 'Dengue', 'count': 0, 'percentage': 10},
            {'name': 'Outras', 'count': 0, 'percentage': 10}
        ]

def get_ai_tips():
    """Dicas da IA"""
    total_patients = Patient.query.count()
    total_consultations = Consultation.query.count()
    
    tips = []
    
    if total_patients == 0:
        tips.append("🎯 Comece a registar os seus primeiros pacientes")
    elif total_patients < 5:
        tips.append(f"📊 Você tem {total_patients} pacientes. Continue registando!")
    else:
        tips.append(f"📈 Ótimo trabalho! Você tem {total_patients} pacientes no Sistema")
    
    if total_consultations == 0:
        tips.append("🩺 Inicie uma Consulta para começar a usar a IA")
    else:
        tips.append(f"🤖 A IA analisou {total_consultations} consultas no total")
    
    tips.append("🔬 Use a IA para analisar sintomas e obter sugestões de Diagnóstico")
    tips.append("📸 Anexe imagens e Exames para um Histórico mais completo")
    
    return tips[:4]