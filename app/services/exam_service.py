import os
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import datetime
from app.extensions.db import db
from app.models.exam import Exam

def allowed_file(filename):
    """Verificar se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, patient_id, consultation_id=None):
    """Salvar arquivo e retornar informações"""
    if file and allowed_file(file.filename):
        # Gerar nome seguro
        original_name = file.filename
        extension = original_name.rsplit('.', 1)[1].lower()
        secure_name = secure_filename(f"patient_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}")
        
        # Criar pasta se não existir
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Salvar arquivo
        file_path = os.path.join(upload_folder, secure_name)
        file.save(file_path)
        
        # Tamanho do arquivo
        file_size = os.path.getsize(file_path)
        
        return {
            'file_path': f"uploads/{secure_name}",
            'file_name': original_name,
            'file_size': file_size
        }
    return None

def add_exam(patient_id, exam_type, exam_name, results, notes, file, consultation_id=None):
    """Adicionar exame ao paciente"""
    file_info = None
    if file and file.filename:
        file_info = save_file(file, patient_id, consultation_id)
    
    exam = Exam(
        patient_id=patient_id,
        consultation_id=consultation_id,
        exam_type=exam_type,
        exam_name=exam_name,
        results=results,
        notes=notes,
        file_path=file_info['file_path'] if file_info else None,
        file_name=file_info['file_name'] if file_info else None,
        file_size=file_info['file_size'] if file_info else None
    )
    
    db.session.add(exam)
    db.session.commit()
    return exam

def get_exams_by_patient(patient_id):
    """Listar todos exames de um paciente"""
    return Exam.query.filter_by(patient_id=patient_id).order_by(Exam.exam_date.desc()).all()

def get_exam_by_id(exam_id):
    """Buscar exame por ID"""
    return Exam.query.get(exam_id)

def delete_exam(exam_id):
    """Eliminar exame (e arquivo se existir)"""
    exam = get_exam_by_id(exam_id)
    if exam:
        # Apagar arquivo físico
        if exam.file_path:
            file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                          exam.file_path.replace('uploads/', ''))
            if os.path.exists(file_full_path):
                os.remove(file_full_path)
        
        db.session.delete(exam)
        db.session.commit()
        return True
    return False