from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.services import user_service
from app.extensions.db import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'jpg', 'jpeg', 'png'}

@profile_bp.route("/")
@login_required
def index():
    """Página de perfil"""
    specialties = user_service.get_specialties()
    hospitals = user_service.get_hospitals()
    return render_template("profile/index.html", 
                         user=current_user, 
                         specialties=specialties, 
                         hospitals=hospitals)

@profile_bp.route("/edit", methods=["POST"])
@login_required
def edit():
    """Editar perfil"""
    name = request.form.get("name")
    email = request.form.get("email")
    specialty = request.form.get("specialty")
    hospital = request.form.get("hospital")
    
    if not name or not email:
        flash("Nome e email são obrigatórios.", "danger")
        return redirect(url_for("profile.index"))
    
    user_service.update_user_profile(current_user, name, email, specialty, hospital)
    flash("Perfil atualizado com sucesso!", "success")
    return redirect(url_for("profile.index"))

@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """Alterar password"""
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    
    if not old_password or not new_password:
        flash("Preencha todos os campos.", "danger")
        return redirect(url_for("profile.index"))
    
    if new_password != confirm_password:
        flash("As Palavras-passe não coincidem.", "danger")
        return redirect(url_for("profile.index"))
    
    success, message = user_service.change_password(current_user, old_password, new_password)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for("profile.index"))



@profile_bp.route("/request-verification", methods=["POST"])
@login_required
def request_verification():
    """Médico solicita verificação com documentos"""
    
    # Verificar se já tem pedido pendente
    if current_user.verification_status == 'pending':
        flash("Você já possui um pedido de verificação pendente. Aguarde a análise do administrador.", "warning")
        return redirect(url_for("profile.index"))
    
    if current_user.is_verified:
        flash("A sua conta já está verificada!", "info")
        return redirect(url_for("profile.index"))
    
    license_number = request.form.get("license_number")
    file = request.files.get("verification_document")
    
    if not license_number or not file:
        flash("Preencha todos os campos e anexe o documento.", "danger")
        return redirect(url_for("profile.index"))
    
    # Salvar documento
    if file and allowed_file(file.filename):
        original_name = secure_filename(file.filename)
        extension = original_name.rsplit('.', 1)[1].lower()
        secure_name = secure_filename(f"verification_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}")
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, secure_name)
        file.save(file_path)
        
        # Atualizar o utilizador
        current_user.license_number = license_number
        current_user.document_path = f"uploads/{secure_name}"
        current_user.verification_requested_at = datetime.now()
        current_user.verification_status = 'pending'  # <-- Mudar status para pendente
        
        db.session.commit()
        
        flash("Solicitação de verificação enviada! Aguarde a análise do Administrador.", "success")
    else:
        flash("Formato de Documento inválido. Use PDF, JPG ou PNG.", "danger")
    
    return redirect(url_for("profile.index"))