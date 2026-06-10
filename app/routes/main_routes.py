from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services import statistics_service
from datetime import datetime

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Estatísticas reais
    stats = statistics_service.get_dashboard_stats(doctor_id=current_user.id)
    
    # Mostrar no terminal para debug
    print(f"DEBUG - Total pacientes: {stats['total_patients']}")
    print(f"DEBUG - Consultas hoje: {stats['today_consultations']}")
    print(f"DEBUG - Exames pendentes: {stats['pending_exams']}")
    print(f"DEBUG - Análises IA hoje: {stats['ai_analyses_today']}")
    
    recent_patients = statistics_service.get_recent_patients(doctor_id=current_user.id, limit=5)
    disease_stats = statistics_service.get_disease_statistics()
    ai_tips = statistics_service.get_ai_tips()
    
    return render_template(
        "dashboard.html",
        stats=stats,
        recent_patients=recent_patients,
        disease_stats=disease_stats,
        ai_tips=ai_tips,
        now=datetime.now()
    )