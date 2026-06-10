from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.decorators import admin_required, super_admin_required
from app.services import admin_service, user_service
from app.extensions.db import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory, current_app
from app.services.notification_service import get_user_notifications, mark_as_read, mark_all_as_read, get_unread_count


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ============ DASHBOARD ADMIN ============

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    """Painel principal do administrador"""
    stats = admin_service.get_system_stats()
    pending_doctors = admin_service.get_pending_verification_requests() 
    return render_template("admin/dashboard.html", stats=stats, pending_doctors=pending_doctors)

# ============ GESTÃO DE MÉDICOS ============

@admin_bp.route("/doctors")
@login_required
@admin_required
def list_doctors():
    """Listar todos os médicos com pesquisa"""
    status = request.args.get('status', 'all')
    role = request.args.get('role', None)
    search = request.args.get('search', '')
    
    # Buscar médicos
    if status == 'pending':
        doctors = admin_service.get_all_doctors(status='pending')
    elif status == 'verified':
        doctors = admin_service.get_all_doctors(status='verified')
    elif status == 'inactive':
        doctors = admin_service.get_all_doctors(status='inactive')
    else:
        doctors = admin_service.get_all_doctors(role=role)
    
    # Aplicar pesquisa por nome ou email
    if search:
        doctors = [d for d in doctors if search.lower() in d.name.lower() or search.lower() in d.email.lower()]
    
    # Se NÃO for Super Admin, remover Super Admin da lista
    if not current_user.is_super_admin():
        doctors = [d for d in doctors if d.role != 'super_admin']
    
    return render_template("admin/doctors.html", doctors=doctors, current_status=status, search=search)



@admin_bp.route("/doctor/<int:doctor_id>")
@login_required
@admin_required
def view_doctor(doctor_id):
    """Ver detalhes do médico"""
    doctor = admin_service.get_doctor_by_id(doctor_id)
    
    if not doctor:
        flash("Médico não encontrado.", "danger")
        return redirect(url_for("admin.list_doctors"))
    
    # Se não for Super Admin, não pode ver Super Admin
    if not current_user.is_super_admin() and doctor.role == 'super_admin':
        flash("Não tem permissão para aceder a este perfil.", "danger")
        return redirect(url_for("admin.list_doctors"))
    
    # Se for Super Admin tentando ver a si próprio, pode (mas com restrições)
    is_self = (doctor.id == current_user.id)
    
    return render_template("admin/doctor_view.html", doctor=doctor, is_self=is_self)

@admin_bp.route("/doctor/<int:doctor_id>/verify", methods=["POST"])
@login_required
@admin_required
def verify_doctor(doctor_id):
    """Verificar médico"""
    notes = request.form.get("notes")
    doctor = admin_service.get_doctor_by_id(doctor_id)
    
    if doctor:
        doctor.is_verified = True
        doctor.verified_by = current_user.id
        doctor.verified_at = datetime.now()
        doctor.verification_status = 'approved'  # <-- Mudar status
        doctor.verification_notes = notes
        db.session.commit()
        flash(f"Médico {doctor.name} verificado com sucesso!", "success")
        
        # TODO: Enviar email de notificação (opcional)
    else:
        flash("Erro ao verificar médico.", "danger")
    
    return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))

@admin_bp.route("/doctor/<int:doctor_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_doctor(doctor_id):
    """Rejeitar médico"""
    notes = request.form.get("notes")
    doctor = admin_service.get_doctor_by_id(doctor_id)
    
    if doctor:
        doctor.is_verified = False
        doctor.is_active = False
        doctor.verification_status = 'rejected'  # <-- Mudar status
        doctor.verification_notes = notes
        db.session.commit()
        flash(f"Médico {doctor.name} rejeitado e conta desativada.", "warning")
    else:
        flash("Erro ao rejeitar médico.", "danger")
    
    return redirect(url_for("admin.list_doctors"))

@admin_bp.route("/doctor/<int:doctor_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_doctor_status(doctor_id):
    """Ativar/Desativar médico"""
    new_status = admin_service.toggle_doctor_status(doctor_id)
    if new_status is not None:
        status_text = "ativada" if new_status else "desativada"
        flash(f"Conta do médico {status_text} com sucesso!", "success")
    else:
        flash("Erro ao alterar status.", "danger")
    
    return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))

@admin_bp.route("/doctor/<int:doctor_id>/change-role", methods=["POST"])
@login_required
@admin_required  # Qualquer Admin (não precisa ser Super Admin)
def change_doctor_role(doctor_id):
    """Alterar role do médico (Admin ou Médico)"""
    doctor = admin_service.get_doctor_by_id(doctor_id)
    
    if not doctor:
        flash("Médico não encontrado.", "danger")
        return redirect(url_for("admin.list_doctors"))
    
    # Não pode alterar Super Admin
    if doctor.role == 'super_admin':
        flash("Não é possível alterar o role de um Super Administrador.", "danger")
        return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))
    
    # Não pode alterar a si próprio (evitar remover próprio admin)
    if doctor.id == current_user.id:
        flash("Não pode alterar a sua própria role.", "danger")
        return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))
    
    new_role = request.form.get("role")
    
    if new_role not in ['medico', 'admin']:
        flash("Role inválida.", "danger")
        return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))
    
    doctor.role = new_role
    db.session.commit()
    
    flash(f"Role de {doctor.name} alterada para {new_role}!", "success")
    return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))

# ============ ESTATÍSTICAS AVANÇADAS ============

@admin_bp.route("/statistics")
@login_required
@admin_required
def statistics():
    """Estatísticas detalhadas do sistema"""
    stats = admin_service.get_system_stats()
    return render_template("admin/statistics.html", stats=stats)

# ============ FUNÇÕES PREMIUM (Super Admin) ============

@admin_bp.route("/premium")
@login_required
@super_admin_required
def premium_settings():
    """Configurações de funcionalidades premium"""
    return render_template("admin/premium.html")


# ============ AÇÕES AVANÇADAS ============

@admin_bp.route("/doctor/<int:doctor_id>/suspend", methods=["POST"])
@login_required
@admin_required
def suspend_doctor(doctor_id):
    """Suspender médico temporariamente"""
    doctor = admin_service.get_doctor_by_id(doctor_id)
    if doctor and doctor.id != current_user.id:
        doctor.is_active = False
        db.session.commit()
        flash(f"Médico {doctor.name} suspenso com sucesso!", "warning")
    else:
        flash("Não é possível suspender este médico.", "danger")
    return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))

@admin_bp.route("/doctor/<int:doctor_id>/delete", methods=["POST"])
@login_required
@super_admin_required
def delete_doctor(doctor_id):
    """Eliminar médico permanentemente (apenas Super Admin)"""
    doctor = admin_service.get_doctor_by_id(doctor_id)
    if doctor and doctor.id != current_user.id:
        db.session.delete(doctor)
        db.session.commit()
        flash(f"Médico {doctor.name} eliminado permanentemente!", "danger")
    else:
        flash("Não é possível eliminar este médico.", "danger")
    return redirect(url_for("admin.list_doctors"))

@admin_bp.route("/doctor/<int:doctor_id>/reset-password", methods=["POST"])
@login_required
@admin_required
def reset_doctor_password(doctor_id):
    """Resetar password do médico"""
    doctor = admin_service.get_doctor_by_id(doctor_id)
    if doctor:
        new_password = request.form.get("new_password")
        if new_password and len(new_password) >= 6:
            doctor.set_password(new_password)
            db.session.commit()
            flash(f"Password do médico {doctor.name} foi redefinida!", "success")
        else:
            flash("A nova password deve ter pelo menos 6 caracteres.", "danger")
    return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))

@admin_bp.route("/doctor/<int:doctor_id>/download-document")
@login_required
@admin_required
def download_document(doctor_id):
    """Baixar documento de verificação do médico"""
    doctor = admin_service.get_doctor_by_id(doctor_id)
    if doctor and doctor.document_path:
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            doctor.document_path.replace('uploads/', '')
        )
    flash("Documento não encontrado.", "danger")
    return redirect(url_for("admin.view_doctor", doctor_id=doctor_id))
    

@admin_bp.route("/notifications")
@login_required
@admin_required
def notifications_page():
    """Página de notificações do admin"""
    notifications = get_user_notifications(current_user.id, limit=50)
    unread_count = get_unread_count(current_user.id)
    return render_template("admin/notifications_page.html", notifications=notifications, unread_count=unread_count)

@admin_bp.route("/notifications/mark-read/<int:notification_id>")
@login_required
@admin_required
def mark_notification_read(notification_id):
    """Marcar notificação como lida"""
    mark_as_read(notification_id)
    return redirect(url_for("admin.notifications_page"))

@admin_bp.route("/notifications/mark-all-read")
@login_required
@admin_required
def mark_all_notifications_read():
    """Marcar todas notificações como lidas"""
    mark_all_as_read(current_user.id)
    flash("Todas as notificações foram marcadas como lidas.", "success")
    return redirect(url_for("admin.notifications_page"))

