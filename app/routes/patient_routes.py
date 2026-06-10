from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.history_service import get_patient_history, generate_clinical_summary
from app.services import patient_service
from app.extensions.db import db

patient_bp = Blueprint("patient", __name__, url_prefix="/patients")

# LISTAR PACIENTES
@patient_bp.route("/")
@login_required
def list_patients():
    search = request.args.get('search', '')
    if search:
        patients = patient_service.search_patients(search)
    else:
        patients = patient_service.get_all_patients()
    return render_template("patients/list.html", patients=patients, search=search)

# CRIAR PACIENTE
@patient_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_patient():
    if request.method == "POST":
        name = request.form.get("name")
        identification = request.form.get("identification")
        age = request.form.get("age")
        gender = request.form.get("gender")
        contact = request.form.get("contact")
        
        # Validações
        if not name:
            flash("Nome do paciente é obrigatório.", "danger")
            return redirect(url_for("patient.create_patient"))
        
        # Verificar se BI/NIF já existe (se foi preenchido)
        if identification:
            existing = patient_service.get_patient_by_identification(identification)
            if existing:
                flash(f"Já existe um paciente com o BI/NIF: {identification}", "danger")
                return redirect(url_for("patient.create_patient"))
        
        patient = patient_service.create_patient(name, identification, age, gender, contact)
        flash(f"Paciente {patient.name} criado com sucesso!", "success")
        return redirect(url_for("patient.list_patients"))
    
    return render_template("patients/create.html")

# VER PERFIL DO PACIENTE
@patient_bp.route("/<int:patient_id>")
@login_required
def view_patient(patient_id):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    return render_template("patients/view.html", patient=patient)

# EDITAR PACIENTE
@patient_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    if request.method == "POST":
        name = request.form.get("name")
        identification = request.form.get("identification")
        age = request.form.get("age")
        gender = request.form.get("gender")
        contact = request.form.get("contact")
        
        # Verificar se o novo BI/NIF já pertence a outro paciente
        if identification and identification != patient.identification:
            existing = patient_service.get_patient_by_identification(identification)
            if existing:
                flash(f"Já existe outro paciente com o BI/NIF: {identification}", "danger")
                return redirect(url_for("patient.edit_patient", patient_id=patient.id))
        
        patient_service.update_patient(patient, name, identification, age, gender, contact)
        flash(f"Paciente {patient.name} atualizado com sucesso!", "success")
        return redirect(url_for("patient.view_patient", patient_id=patient.id))
    
    return render_template("patients/edit.html", patient=patient)

# ELIMINAR PACIENTE
@patient_bp.route("/<int:patient_id>/delete", methods=["POST"])
@login_required
def delete_patient(patient_id):
    patient = patient_service.get_patient_by_id(patient_id)
    if patient:
        name = patient.name
        patient_service.delete_patient(patient)
        flash(f"Paciente {name} eliminado.", "info")
    return redirect(url_for("patient.list_patients"))


@patient_bp.route("/<int:patient_id>/history")
@login_required
def patient_history(patient_id):
    """Ver histórico clínico completo do paciente"""
    
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    history = get_patient_history(patient_id)
    summary = generate_clinical_summary(patient_id)
    
    return render_template("patients/history.html", 
                         patient=patient, 
                         history=history, 
                         summary=summary)


@patient_bp.route("/<int:patient_id>/add-condition", methods=["POST"])
@login_required
def add_chronic_condition(patient_id):
    """Adicionar condição crónica ao paciente"""
    from app.services.history_service import add_to_medical_history
    
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    condition = request.form.get("condition")
    notes = request.form.get("notes")
    treatment = request.form.get("treatment")
    
    if not condition:
        flash("Por favor, descreva a condição crónica.", "danger")
        return redirect(url_for("patient.patient_history", patient_id=patient_id))
    
    add_to_medical_history(
        patient_id=patient_id,
        condition=condition,
        notes=notes,
        treatment=treatment
    )
    
    flash(f"Condição crónica '{condition}' adicionada ao histórico!", "success")
    return redirect(url_for("patient.patient_history", patient_id=patient_id))


@patient_bp.route("/<int:patient_id>/delete-condition/<int:history_id>", methods=["POST"])
@login_required
def delete_chronic_condition(patient_id, history_id):
    """Eliminar condição crónica"""
    from app.models.medical_history import MedicalHistory
    
    history = MedicalHistory.query.get(history_id)
    if history and history.patient_id == patient_id:
        db.session.delete(history)
        db.session.commit()
        flash("Condição crónica removida!", "success")
    else:
        flash("Registo não encontrado.", "danger")
    
    return redirect(url_for("patient.patient_history", patient_id=patient_id))