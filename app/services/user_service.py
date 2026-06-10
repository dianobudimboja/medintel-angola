from app.models.user import User
from app.extensions.db import db
from flask_login import current_user

def get_user_by_id(user_id):
    """Buscar médico por ID"""
    return User.query.get(user_id)

def update_user_profile(user, name, email, specialty, hospital):
    """Atualizar perfil do médico"""
    user.name = name
    user.email = email
    user.specialty = specialty
    user.hospital = hospital
    db.session.commit()
    return user

def change_password(user, old_password, new_password):
    """Alterar password do médico"""
    if not user.check_password(old_password):
        return False, "Palavra-passe atual incorreta"
    
    if len(new_password) < 6:
        return False, "A nova Palavra-passe deve ter pelo menos 6 caracteres"
    
    if old_password == new_password:
        return False, "A nova Palavra-passe deve ser diferente da atual"
    
    user.set_password(new_password)
    db.session.commit()
    return True, "Palavra-passe alterada com sucesso"

def get_specialties():
    """Lista de especialidades disponíveis"""
    return [
        'Clínica Geral', 'Pediatria', 'Cardiologia', 'Ginecologia',
        'Infectologia', 'Medicina Interna', 'Cirurgia Geral', 'Ortopedia',
        'Neurologia', 'Dermatologia', 'Psiquiatria', 'Oftalmologia'
    ]

def get_hospitals():
    """Lista de hospitais de Angola"""
    return [
        'Hospital Américo Boavida (Luanda)',
        'Hospital Josina Machel (Luanda)',
        'Clínica Multiperfil (Luanda)',
        'Hospital Geral de Benguela',
        'Hospital Central do Huambo',
        'Hospital Provincial do Namibe',
        'Hospital Municipal do Kilamba',
        'Clínica Sagrada Esperança (Luanda)',
        'Hospital David Bernardino (Luanda)'
    ]