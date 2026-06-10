from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services import patient_service, consultation_service
from datetime import datetime
from app import db
from app.models.consultation import Consultation
from app.services.ai_service import predict_disease

consultation_bp = Blueprint("consultation", __name__, url_prefix="/consultations")

# NOVA CONSULTA
@consultation_bp.route("/new/<int:patient_id>", methods=["GET", "POST"])
@login_required
def new_consultation(patient_id):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        vital_signs = request.form.get("vital_signs")
        observations = request.form.get("observations")
        
        if not symptoms:
            flash("Sintomas são obrigatórios.", "danger")
            return redirect(url_for("consultation.new_consultation", patient_id=patient_id))
        
        consultation = Consultation(
            patient_id=patient_id,
            doctor_id=current_user.id,
            symptoms=symptoms,
            vital_signs=vital_signs,
            observations=observations,
            status="em_andamento",
            consultation_date=datetime.utcnow() 
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        flash(f"Consulta iniciada com sucesso!", "success")
        return redirect(url_for("consultation.view_consultation", consultation_id=consultation.id))
    
    return render_template("consultations/new.html", patient=patient)


# VER CONSULTA
@consultation_bp.route("/<int:consultation_id>")
@login_required
def view_consultation(consultation_id):
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation:
        flash("Consulta não encontrada.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    diagnosis = consultation_service.get_diagnosis_by_consultation(consultation_id)
    patient = patient_service.get_patient_by_id(consultation.patient_id)
    history = consultation_service.get_patient_consultations(consultation.patient_id)
    
    return render_template("consultations/view.html", 
                         consultation=consultation, 
                         diagnosis=diagnosis,
                         patient=patient,
                         history=history)


# ANALISAR COM IA
@consultation_bp.route("/<int:consultation_id>/analyze", methods=["POST"])
@login_required
def analyze_with_ai(consultation_id):
    """Analisar consulta com IA (usando histórico do paciente)"""
    from app.services.ai_service import predict_disease
    
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation:
        return jsonify({"error": "Consulta não encontrada"}), 404
    
    if not consultation.symptoms:
        return jsonify({"error": "Nenhum sintoma registado para análise"}), 400
    
    # Passar o patient_id para a IA usar o histórico
    ai_result = predict_disease(consultation.symptoms, consultation.patient_id)
    
    return jsonify(ai_result)



# FINALIZAR CONSULTA COM DIAGNÓSTICO
@consultation_bp.route("/<int:consultation_id>/diagnose", methods=["GET", "POST"])
@login_required
def add_diagnosis(consultation_id):
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation:
        flash("Consulta não encontrada.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    patient = patient_service.get_patient_by_id(consultation.patient_id)
    
    if request.method == "POST":
        doctor_diagnosis = request.form.get("doctor_diagnosis")
        doctor_notes = request.form.get("doctor_notes")
        prescribed_medication = request.form.get("prescribed_medication")
        recommendations = request.form.get("recommendations")
        ai_suggestion_json = request.form.get("ai_suggestion")
        
        import json
        ai_suggestion = json.loads(ai_suggestion_json) if ai_suggestion_json else None
        
        consultation_service.create_diagnosis(
            consultation_id=consultation_id,
            doctor_diagnosis=doctor_diagnosis,
            ai_suggestion=ai_suggestion,
            doctor_notes=doctor_notes,
            prescribed_medication=prescribed_medication,
            recommendations=recommendations
        )
        
        flash(f"Diagnóstico registado para {patient.name}!", "success")
        return redirect(url_for("patient.view_patient", patient_id=patient.id))
    
    return render_template("consultations/diagnose.html", 
                         consultation=consultation, 
                         patient=patient)

# ADICIONAR EXAME
@consultation_bp.route("/<int:consultation_id>/add-exam", methods=["POST"])
@login_required
def add_exam(consultation_id):
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation:
        flash("Consulta não encontrada.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    exam_type = request.form.get("exam_type")
    exam_name = request.form.get("exam_name")
    results = request.form.get("results")
    
    consultation_service.add_exam(
        patient_id=consultation.patient_id,
        exam_type=exam_type,
        exam_name=exam_name,
        results=results,
        consultation_id=consultation_id
    )
    
    flash("Exame adicionado com sucesso!", "success")
    return redirect(url_for("consultation.view_consultation", consultation_id=consultation_id))


@consultation_bp.route("/today")
@login_required
def today_consultations():
    """Listar consultas de hoje"""
    from datetime import datetime
    
    today = datetime.now().date()
    today_start = datetime(today.year, today.month, today.day, 0, 0, 0)
    today_end = datetime(today.year, today.month, today.day, 23, 59, 59)
    
    consultations = Consultation.query.filter(
        Consultation.consultation_date >= today_start,
        Consultation.consultation_date <= today_end
    ).order_by(Consultation.consultation_date.desc()).all()
    
    return render_template("consultations/today.html", consultations=consultations, today=today)




