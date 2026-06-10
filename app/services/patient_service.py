from app.models.patient import Patient
from app.extensions.db import db

def create_patient(name, identification, age, gender, contact):
    """Criar novo paciente com BI/NIF"""
    patient = Patient(
        name=name,
        identification=identification if identification else None,
        age=age if age else None,
        gender=gender,
        contact=contact
    )
    db.session.add(patient)
    db.session.commit()
    return patient

def get_all_patients():
    """Listar todos os pacientes"""
    return Patient.query.all()

def get_patient_by_id(patient_id):
    """Buscar paciente por ID"""
    return Patient.query.get(patient_id)

def get_patient_by_identification(identification):
    """Buscar paciente por BI/NIF (útil para evitar duplicados)"""
    return Patient.query.filter_by(identification=identification).first()

def update_patient(patient, name, identification, age, gender, contact):
    """Atualizar dados do paciente"""
    patient.name = name
    patient.identification = identification if identification else None
    patient.age = age if age else None
    patient.gender = gender
    patient.contact = contact
    db.session.commit()
    return patient

def delete_patient(patient):
    """Eliminar paciente"""
    db.session.delete(patient)
    db.session.commit()

def search_patients(search_term):
    """Pesquisar pacientes por nome, identificação ou contacto"""
    return Patient.query.filter(
        Patient.name.ilike(f'%{search_term}%') |
        Patient.identification.ilike(f'%{search_term}%') |
        Patient.contact.ilike(f'%{search_term}%')
    ).all()

def get_patient_count():
    """Contar total de pacientes"""
    return Patient.query.count()