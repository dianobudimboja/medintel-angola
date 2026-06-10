from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, jsonify
from flask_login import login_required
from app.services import exam_service, patient_service, consultation_service
from app.extensions.db import db
from app.models import Exam
from datetime import datetime
import json
import os
import traceback

exam_bp = Blueprint("exam", __name__, url_prefix="/exams")

# LISTAR EXAMES DO PACIENTE
@exam_bp.route("/patient/<int:patient_id>")
@login_required
def list_patient_exams(patient_id):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    exams = exam_service.get_exams_by_patient(patient_id)
    return render_template("exams/list.html", patient=patient, exams=exams)


# ADICIONAR EXAME
@exam_bp.route("/add/<int:patient_id>", methods=["GET", "POST"])
@login_required
def add_exam(patient_id):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        flash("Paciente não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    consultation_id = request.args.get('consultation_id', None)
    
    if request.method == "POST":
        exam_type = request.form.get("exam_type")
        exam_name = request.form.get("exam_name")
        results = request.form.get("results")
        notes = request.form.get("notes")
        file = request.files.get("exam_file")
        
        if not exam_type:
            flash("O tipo de exame é obrigatório.", "danger")
            return redirect(url_for("exam.add_exam", patient_id=patient_id))
        
        exam = exam_service.add_exam(
            patient_id=patient_id,
            exam_type=exam_type,
            exam_name=exam_name,
            results=results,
            notes=notes,
            file=file,
            consultation_id=consultation_id
        )
        
        # Analisar automaticamente se for imagem
        if exam.file_path and exam.file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            from app.services.image_analysis_service import analyze_exam_image
            import os
            from flask import current_app
            import json
            from datetime import datetime
            
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], exam.file_path.replace('uploads/', ''))
            if os.path.exists(full_path):
                try:
                    analysis_result = analyze_exam_image(full_path)
                    exam.ai_analyzed = True
                    exam.ai_analysis_date = datetime.now()
                    exam.ai_findings = analysis_result.get('findings', '')
                    exam.ai_confidence = analysis_result.get('confidence', 0)
                    exam.ai_recommendations = json.dumps(analysis_result.get('recommendations', []))
                    db.session.commit()
                    flash(f"Exame adicionado e analisado pela IA! Confiança: {exam.ai_confidence}%", "success")
                except Exception as e:
                    print(f"Erro na análise automática: {e}")
                    flash("Exame adicionado, mas a análise IA falhou.", "warning")
        
        flash(f"Exame {exam.exam_name or exam.exam_type} adicionado com sucesso!", "success")
        
        if consultation_id:
            return redirect(url_for("consultation.view_consultation", consultation_id=consultation_id))
        return redirect(url_for("exam.list_patient_exams", patient_id=patient_id))
    
    return render_template("exams/add.html", patient=patient, consultation_id=consultation_id)



# VER EXAME
@exam_bp.route("/view/<int:exam_id>")
@login_required
def view_exam(exam_id):
    exam = exam_service.get_exam_by_id(exam_id)
    if not exam:
        flash("Exame não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    return render_template("exams/view.html", exam=exam)


# ELIMINAR EXAME
@exam_bp.route("/delete/<int:exam_id>", methods=["POST"])
@login_required
def delete_exam(exam_id):
    exam = exam_service.get_exam_by_id(exam_id)
    if exam:
        patient_id = exam.patient_id
        exam_service.delete_exam(exam_id)
        flash("Exame eliminado com sucesso.", "success")
        return redirect(url_for("exam.list_patient_exams", patient_id=patient_id))
    
    flash("Exame não encontrado.", "danger")
    return redirect(url_for("patient.list_patients"))


# VISUALIZAR IMAGEM
@exam_bp.route("/image/<filename>")
@login_required
def view_image(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)


@exam_bp.route("/<int:exam_id>/analyze", methods=["POST"])
@login_required
def analyze_exam(exam_id):
    """Analisar exame com IA (usando histórico do paciente)"""
    from app.services.image_analysis_service import analyze_exam_image
    
    exam = exam_service.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"error": "Exame não encontrado"}), 404
    
    if not exam.file_path:
        return jsonify({"error": "Exame sem imagem para análise"}), 400
    
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], exam.file_path.replace('uploads/', ''))
    
    if not os.path.exists(full_path):
        return jsonify({"error": "Ficheiro de imagem não encontrado"}), 404
    
    try:
        # Passar patient_id para usar histórico
        analysis_result = analyze_exam_image(full_path, exam.patient_id)
        
        # Guardar no banco
        exam.ai_analyzed = True
        exam.ai_analysis_date = datetime.now()
        exam.ai_findings = analysis_result.get('findings', '')
        exam.ai_confidence = analysis_result.get('confidence', 0)
        exam.ai_recommendations = json.dumps(analysis_result.get('recommendations', []))
        
        if 'diagnosis' in analysis_result:
            exam.ai_diagnosis = analysis_result['diagnosis']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Erro na análise: {str(e)}"}), 500



@exam_bp.route("/<int:exam_id>/update-results", methods=["POST"])
@login_required
def update_results(exam_id):
    """Atualizar resultados do exame"""
    exam = exam_service.get_exam_by_id(exam_id)
    if not exam:
        flash("Exame não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    results = request.form.get("results")
    exam.results = results
    db.session.commit()
    
    flash("Resultados atualizados com sucesso!", "success")
    return redirect(url_for("exam.view_exam", exam_id=exam_id))



@exam_bp.route("/<int:exam_id>/update-notes", methods=["POST"])
@login_required
def update_notes(exam_id):
    """Atualizar observações do exame"""
    exam = exam_service.get_exam_by_id(exam_id)
    if not exam:
        flash("Exame não encontrado.", "danger")
        return redirect(url_for("patient.list_patients"))
    
    notes = request.form.get("notes")
    exam.notes = notes
    db.session.commit()
    
    flash("Observações atualizadas com sucesso!", "success")
    return redirect(url_for("exam.view_exam", exam_id=exam_id))



@exam_bp.route("/pending")
@login_required
def pending_exams():
    """Listar exames pendentes"""
    from datetime import datetime, timedelta
    
    week_ago = datetime.now() - timedelta(days=7)
    
    pending = Exam.query.filter(
        (Exam.results == None) | (Exam.results == ''),
        Exam.created_at >= week_ago
    ).order_by(Exam.created_at.desc()).all()
    
    return render_template("exams/pending.html", exams=pending)
