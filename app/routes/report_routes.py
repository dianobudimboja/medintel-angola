from flask import Blueprint, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services import pdf_service, patient_service, consultation_service
from app.services.exam_service import get_exams_by_patient
from io import BytesIO

report_bp = Blueprint("report", __name__, url_prefix="/reports")

@report_bp.route("/patient/<int:patient_id>")
@login_required
def patient_report(patient_id):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    consultations = consultation_service.get_patient_consultations(patient_id)
    exams = get_exams_by_patient(patient_id)
    
    pdf_data = pdf_service.generate_patient_report(patient, consultations, exams)
    
    if pdf_data is None:
        flash("Erro ao gerar Relatório PDF.", "danger")
        return redirect(url_for("patient.view_patient", patient_id=patient_id))
    
    return send_file(
        BytesIO(pdf_data),
        as_attachment=True,
        download_name=f"paciente_{patient.id}_{patient.name}.pdf",
        mimetype='application/pdf'
    )

@report_bp.route("/consultation/<int:consultation_id>")
@login_required
def consultation_report(consultation_id):
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation:
        flash("Consulta não encontrada.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    patient = patient_service.get_patient_by_id(consultation.patient_id)
    diagnosis = consultation_service.get_diagnosis_by_consultation(consultation_id)
    
    pdf_data = pdf_service.generate_consultation_report(consultation, patient, diagnosis)
    
    if pdf_data is None:
        flash("Erro ao gerar Relatório PDF.", "danger")
        return redirect(url_for("consultation.view_consultation", consultation_id=consultation_id))
    
    return send_file(
        BytesIO(pdf_data),
        as_attachment=True,
        download_name=f"consulta_{consultation_id}_{patient.name}.pdf",
        mimetype='application/pdf'
    )