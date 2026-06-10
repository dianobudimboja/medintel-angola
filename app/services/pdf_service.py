from xhtml2pdf import pisa
from flask import render_template
from datetime import datetime
import io
import os

def generate_patient_report(patient, consultations, exams):
    """Gerar relatório PDF do paciente usando xhtml2pdf"""
    
    # Preparar dados para o template
    data = {
        'patient': patient,
        'consultations': consultations,
        'exams': exams,
        'generated_date': datetime.now(),
    }
    
    # Renderizar template HTML
    html_string = render_template('reports/patient_report.html', **data)
    
    # Converter para PDF
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)
    
    if pisa_status.err:
        return None
    
    pdf_file.seek(0)
    return pdf_file.getvalue()

def generate_consultation_report(consultation, patient, diagnosis):
    """Gerar relatório PDF de uma consulta específica"""
    
    data = {
        'consultation': consultation,
        'patient': patient,
        'diagnosis': diagnosis,
        'generated_date': datetime.now()
    }
    
    html_string = render_template('reports/consultation_report.html', **data)
    
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)
    
    if pisa_status.err:
        return None
    
    pdf_file.seek(0)
    return pdf_file.getvalue()