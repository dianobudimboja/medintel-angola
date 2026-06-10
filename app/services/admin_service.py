from app.models.user import User
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.exam import Exam
from app.extensions.db import db
from datetime import datetime
from sqlalchemy import func

# ============ GESTÃO DE MÉDICOS ============

def get_all_doctors(status=None, role=None):
    """Listar todos os médicos com filtros"""
    query = User.query
    if status == 'pending':
        query = query.filter_by(is_verified=False, is_active=True)
    elif status == 'verified':
        query = query.filter_by(is_verified=True, is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    if role:
        query = query.filter_by(role=role)
    
    return query.order_by(User.registration_date.desc()).all()

def get_doctor_by_id(doctor_id):
    """Pesquisar médico por ID"""
    return User.query.get(doctor_id)

def verify_doctor(doctor_id, admin_id, notes=None):
    """Verificar médico (tornar credenciais válidas)"""
    doctor = get_doctor_by_id(doctor_id)
    if doctor:
        doctor.is_verified = True
        doctor.verified_by = admin_id
        doctor.verified_at = datetime.utcnow()
        doctor.verification_notes = notes
        db.session.commit()
        return True
    return False

def reject_doctor(doctor_id, notes=None):
    """Rejeitar médico (desativar conta)"""
    doctor = get_doctor_by_id(doctor_id)
    if doctor:
        doctor.is_active = False
        doctor.is_verified = False
        doctor.verification_notes = notes
        db.session.commit()
        return True
    return False

def toggle_doctor_status(doctor_id):
    """Ativar/Desativar médico"""
    doctor = get_doctor_by_id(doctor_id)
    if doctor:
        doctor.is_active = not doctor.is_active
        db.session.commit()
        return doctor.is_active
    return None

def change_doctor_role(doctor_id, new_role):
    """Alterar role do médico (admin, medico)"""
    doctor = get_doctor_by_id(doctor_id)
    if doctor and new_role in ['admin', 'medico']:
        doctor.role = new_role
        db.session.commit()
        return True
    return False

def update_doctor_license(doctor_id, license_number, document_path=None):
    """Atualizar informações de licença do médico"""
    doctor = get_doctor_by_id(doctor_id)
    if doctor:
        doctor.license_number = license_number
        if document_path:
            doctor.document_path = document_path
        db.session.commit()
        return True
    return False

# ============ ESTATÍSTICAS DO SISTEMA ============

def get_system_stats():
    """Estatísticas gerais do sistema"""
    total_doctors = User.query.count()
    verified_doctors = User.query.filter_by(is_verified=True, is_active=True).count()
    pending_doctors = User.query.filter_by(is_verified=False, is_active=True).count()
    inactive_doctors = User.query.filter_by(is_active=False).count()
    
    total_patients = Patient.query.count()
    total_consultations = Consultation.query.count()
    total_exams = Exam.query.count()
    
    # Consultas por mês (últimos 12 meses)
    consultations_by_month = db.session.query(
        func.strftime('%Y-%m', Consultation.consultation_date).label('month'),
        func.count(Consultation.id).label('total')
    ).group_by('month').order_by('month').limit(12).all()
    
    # Exames por mês (últimos 12 meses)
    exams_by_month = db.session.query(
        func.strftime('%Y-%m', Exam.exam_date).label('month'),
        func.count(Exam.id).label('total')
    ).group_by('month').order_by('month').limit(12).all()
    
    # Converter para dicionário para fácil acesso
    exams_dict = {e[0]: e[1] for e in exams_by_month}
    
    # Combinar consultas e exames por mês
    combined_stats = []
    for c in consultations_by_month:
        month = c[0]
        combined_stats.append({
            'month': month,
            'consultations': c[1],
            'exams': exams_dict.get(month, 0)
        })
    
    return {
        'doctors': {
            'total': total_doctors,
            'verified': verified_doctors,
            'pending': pending_doctors,
            'inactive': inactive_doctors
        },
        'patients': {
            'total': total_patients
        },
        'consultations': {
            'total': total_consultations,
            'by_month': combined_stats
        },
        'exams': {
            'total': total_exams
        }
    }



def get_pending_verifications():
    """Médicos pendentes de verificação"""
    return User.query.filter_by(is_verified=False, is_active=True, role='medico').all()

# ============ FUNÇÕES PREMIUM (futuro) ============

def get_premium_stats():
    """Estatísticas para funcionalidades premium"""
    # Placeholder para futuras implementações
    return {
        'ai_analyses': 0,
        'reports_generated': 0,
        'api_calls': 0
    }


def get_pending_verification_requests():
    """Médicos que solicitaram verificação mas ainda não foram verificados"""
    return User.query.filter(
        User.is_verified == False,
        User.is_active == True,
        User.role == 'medico',
        User.verification_requested_at != None
    ).order_by(User.verification_requested_at.asc()).all()