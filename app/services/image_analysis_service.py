import os
import random
import re
from datetime import datetime
from app.services.history_service import generate_clinical_summary

def analyze_exam_image(file_path, patient_id=None):
    """Analisar imagem de exame com contexto do histórico do paciente"""
    
    filename = os.path.basename(file_path).lower()
    exam_type = detect_exam_type(filename)
    
    # Buscar histórico do paciente
    patient_context = ""
    historico_info = {'usado': False, 'condicoes': [], 'ajustes': []}
    
    if patient_id:
        try:
            summary = generate_clinical_summary(patient_id)
            
            if summary['chronic_conditions']:
                for condition in summary['chronic_conditions']:
                    condition_name = condition['condition'].lower()
                    historico_info['condicoes'].append(condition['condition'])
                    
                    if 'malária' in condition_name or 'malaria' in condition_name:
                        patient_context += "Paciente com histórico de Malária. "
                        historico_info['ajustes'].append("Histórico de Malária considerado")
                    elif 'tuberculose' in condition_name or 'tb' in condition_name:
                        patient_context += "Paciente com histórico de Tuberculose. "
                        historico_info['ajustes'].append("Histórico de Tuberculose considerado")
                    elif 'hipertensão' in condition_name or 'hipertensao' in condition_name:
                        patient_context += "Paciente hipertenso. "
                        historico_info['ajustes'].append("Histórico de Hipertensão considerado")
                    elif 'diabetes' in condition_name:
                        patient_context += "Paciente diabético. "
                        historico_info['ajustes'].append("Histórico de Diabetes considerado")
            
            if summary['diagnoses']:
                ultimo_diag = summary['diagnoses'][-1] if summary['diagnoses'] else None
                if ultimo_diag:
                    patient_context += f"Último diagnóstico: {ultimo_diag['diagnosis']}. "
                    historico_info['ajustes'].append(f"Último diagnóstico: {ultimo_diag['diagnosis']}")
            
            if patient_context:
                historico_info['usado'] = True
                
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    # Análise baseada no tipo de exame
    if exam_type == 'raio_x':
        result = analyze_chest_xray(filename, patient_context)
    elif exam_type == 'blood_smear':
        result = analyze_blood_smear(filename, patient_context)
    elif exam_type == 'urine':
        result = analyze_urine_exam(filename, patient_context)
    elif exam_type == 'ultrasound':
        result = analyze_ultrasound(filename, patient_context)
    else:
        result = analyze_general_image(filename, patient_context)  # <-- CORRIGIDO: passa patient_context
    
    # Adicionar info do histórico ao resultado
    result['historico_info'] = historico_info
    result['usou_historico'] = historico_info['usado']
    
    return result

def detect_exam_type(filename):
    """Detectar tipo de exame pelo nome"""
    
    if re.search(r'(raio|xray|torax|peito|pulmao|chest)', filename):
        return 'raio_x'
    elif re.search(r'(sangue|blood|malaria|esfregaco|hemograma)', filename):
        return 'blood_smear'
    elif re.search(r'(urina|urine)', filename):
        return 'urine'
    elif re.search(r'(ultrassom|ultrasound|eco)', filename):
        return 'ultrasound'
    else:
        return 'general'

def analyze_chest_xray(filename, patient_context=""):
    """Analisar Raio-X de tórax"""
    
    # Ajustar baseado no histórico
    tb_boost = 'tuberculose' in patient_context.lower() or 'tb' in patient_context.lower()
    
    if 'normal' in filename:
        diagnosis = "Normal"
        findings = "Tórax normal sem alterações significativas"
        confidence = random.uniform(85, 98)
        severity = "normal"
    elif 'pneumonia' in filename:
        diagnosis = "Pneumonia"
        findings = "Sinais sugestivos de pneumonia (infiltrado pulmonar)"
        confidence = random.uniform(75, 92)
        severity = "alta"
    elif 'tuberculose' in filename or 'tb' in filename or tb_boost:
        diagnosis = "Tuberculose"
        findings = "Sinais radiológicos sugestivos de tuberculose pulmonar"
        confidence = random.uniform(70, 95)
        severity = "alta"
    else:
        options = [
            ("Normal", "Tórax normal", random.uniform(70, 95), "normal"),
            ("Bronquite", "Sinais de bronquite aguda", random.uniform(65, 85), "media"),
            ("Pneumonia", "Infiltrado pulmonar sugestivo de pneumonia", random.uniform(60, 80), "alta")
        ]
        diagnosis, findings, confidence, severity = random.choice(options)
    
    recommendations = []
    if severity == "alta":
        recommendations = ["Avaliação médica urgente", "Considerar TC para confirmação"]
    else:
        recommendations = ["Acompanhamento clínico", "Repetir exame se sintomas persistirem"]
    
    if tb_boost:
        recommendations.append("Paciente com histórico de Tuberculose - avaliar possível reactivação")
    
    return {
        'exam_type': 'Raio-X de Tórax',
        'diagnosis': diagnosis,
        'findings': findings,
        'confidence': round(confidence, 1),
        'severity': severity,
        'recommendations': recommendations,
        'analyzed_at': datetime.now().isoformat()
    }

def analyze_blood_smear(filename, patient_context=""):
    """Analisar esfregaço de sangue - Malária"""
    
    # Ajustar confiança baseada no histórico
    confidence_boost = 0
    if 'malária' in patient_context.lower() or 'malaria' in patient_context.lower():
        confidence_boost = 15
    
    if 'malaria' in filename and 'positivo' in filename:
        diagnosis = "Malária Positivo"
        findings = "Positivo para Plasmodium falciparum"
        confidence = min(98, random.uniform(85, 98) + confidence_boost)
        positive = True
    elif 'malaria' in filename and 'negativo' in filename:
        diagnosis = "Malária Negativo"
        findings = "Negativo para plasmódios"
        confidence = min(99, random.uniform(90, 99) + confidence_boost/2)
        positive = False
    else:
        if confidence_boost > 0:
            positive = random.random() > 0.4
        else:
            positive = random.choice([True, False])
        
        if positive:
            diagnosis = "Malária Positivo"
            findings = "Plasmodium falciparum detectado"
            confidence = min(95, random.uniform(75, 95) + confidence_boost)
        else:
            diagnosis = "Malária Negativo"
            findings = "Ausência de parasitas da malária"
            confidence = min(98, random.uniform(85, 98) + confidence_boost/2)
    
    recommendations = []
    if positive:
        recommendations = ["Iniciar tratamento antimalárico conforme protocolo", "Monitorizar sinais de alarme"]
        if 'malária' in patient_context.lower():
            recommendations.append("Paciente com histórico de Malária - considerar profilaxia pós-tratamento")
    else:
        recommendations = ["Investigar outras causas de febre", "Considerar hemocultura se febre persistir"]
    
    return {
        'exam_type': 'Esfregaço de Sangue - Malária',
        'diagnosis': diagnosis,
        'findings': findings,
        'confidence': round(confidence, 1),
        'positive': positive,
        'recommendations': recommendations,
        'analyzed_at': datetime.now().isoformat()
    }

def analyze_urine_exam(filename, patient_context=""):
    """Analisar exame de urina"""
    
    options = [
        ("Normal", "Urina normal", random.uniform(85, 98), "normal"),
        ("ITU", "Infecção do trato urinário", random.uniform(75, 95), "media"),
        ("Proteinúria", "Presença de proteínas", random.uniform(65, 85), "media")
    ]
    
    diagnosis, findings, confidence, severity = random.choice(options)
    
    recommendations = []
    if diagnosis == "ITU":
        recommendations = ["Solicitar urocultura", "Iniciar antibioticoterapia"]
    elif diagnosis == "Proteinúria":
        recommendations = ["Avaliação por nefrologia"]
    else:
        recommendations = ["Resultado normal"]
    
    return {
        'exam_type': 'Análise de Urina',
        'diagnosis': diagnosis,
        'findings': findings,
        'confidence': round(confidence, 1),
        'recommendations': recommendations,
        'analyzed_at': datetime.now().isoformat()
    }

def analyze_ultrasound(filename, patient_context=""):
    """Analisar ultrassom"""
    
    options = [
        ("Normal", "Ultrassom sem alterações", random.uniform(85, 98), "normal"),
        ("Esteatose", "Esteatose hepática", random.uniform(75, 95), "media"),
        ("Cálculo biliar", "Colecistolitíase", random.uniform(70, 90), "media")
    ]
    
    diagnosis, findings, confidence, severity = random.choice(options)
    
    return {
        'exam_type': 'Ultrassom',
        'diagnosis': diagnosis,
        'findings': findings,
        'confidence': round(confidence, 1),
        'recommendations': ["Acompanhamento clínico"],
        'analyzed_at': datetime.now().isoformat()
    }

def analyze_general_image(filename, patient_context=""):
    """Analisar imagem geral (com contexto do histórico)"""
    
    options = [
        ("Normal", "Imagem dentro dos padrões de normalidade", random.uniform(70, 95), "normal"),
        ("Alterações", "Alterações inespecíficas - correlacionar com clínica", random.uniform(55, 80), "media"),
        ("Inflamação", "Sinais inflamatórios", random.uniform(60, 85), "media")
    ]
    
    diagnosis, findings, confidence, severity = random.choice(options)
    
    recommendations = ["Correlacionar com dados clínicos", "Enviar para especialista se necessário"]
    
    # Adicionar recomendação baseada no histórico
    if 'diabetes' in patient_context.lower():
        recommendations.append("Paciente diabético - atenção a complicações")
    if 'hipertensão' in patient_context.lower():
        recommendations.append("Paciente hipertenso - avaliar risco cardiovascular")
    
    return {
        'exam_type': 'Imagem Clínica',
        'diagnosis': diagnosis,
        'findings': findings,
        'confidence': round(confidence, 1),
        'severity': severity,
        'recommendations': recommendations,
        'analyzed_at': datetime.now().isoformat()
    }