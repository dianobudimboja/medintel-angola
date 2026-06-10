import joblib
import numpy as np
import pandas as pd
import os
import threading
from flask import current_app
from app.services.history_service import generate_clinical_summary

_model = None
_label_encoder = None
_loading = False

def load_model_async():
    """Carregar modelo em background"""
    global _model, _label_encoder, _loading
    
    if _loading or _model is not None:
        return
    
    _loading = True
    
    def _load():
        global _model, _label_encoder, _loading
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'ai', 'models', 'disease_model.joblib')
            encoder_path = os.path.join(base_dir, 'ai', 'models', 'label_encoder.joblib')
            
            if os.path.exists(model_path) and os.path.exists(encoder_path):
                _model = joblib.load(model_path)
                _label_encoder = joblib.load(encoder_path)
                print("✅ Modelo de IA carregado com sucesso!")
            else:
                print("⚠️ Modelo não encontrado, usando modo simulação")
        except Exception as e:
            print(f"⚠️ Erro ao carregar Modelo: {e}")
        finally:
            _loading = False
    
    thread = threading.Thread(target=_load)
    thread.daemon = True
    thread.start()

def get_model():
    """Obter modelo (carrega se necessário)"""
    global _model, _label_encoder
    if _model is None:
        load_model_async()
    return _model, _label_encoder

def extract_symptoms_vector(symptoms_text):
    """Converter texto para vetor de features"""
    
    symptoms_list = [
        'febre', 'febre_alta', 'dor_de_cabeca', 'dor_atras_olhos',
        'calafrios', 'sudorese', 'sudorese_noturna', 'nausea', 'vomito',
        'dores_musculares', 'dores_articulares', 'fadiga', 'tosse',
        'tosse_persistente', 'tosse_com_sangue', 'dor_garganta',
        'congestao_nasal', 'dor_abdominal', 'dor_peito', 'falta_apetite',
        'perda_peso', 'constipacao', 'diarreia', 'manchas_vermelhas',
        'manchas_rosadas'
    ]
    
    features = {}
    symptoms_lower = symptoms_text.lower()
    
    for symptom in symptoms_list:
        symptom_clean = symptom.replace('_', ' ')
        if symptom_clean in symptoms_lower or symptom in symptoms_lower:
            features[symptom] = 1
        else:
            features[symptom] = 0
    
    return features

def predict_disease(symptoms_text, patient_id=None):
    """Fazer predição usando IA com contexto do histórico do paciente"""
    
    symptoms_lower = symptoms_text.lower()
    
    # Dicionário de doenças e seus sintomas (com pesos)
    disease_keywords = {
        'Malária': {
            'keywords': ['febre', 'calafrios', 'suor', 'dor cabeça', 'nausea', 'vomito', 'dores musculares', 'fadiga', 'arrepios', 'tremores'],
            'peso_forte': ['calafrios', 'febre', 'suor', 'arrepios'],  # Sintomas mais específicos
            'chronic_weight': 1.5
        },
        'Febre Tifoide': {
            'keywords': ['febre alta', 'dor abdominal', 'dor cabeça', 'falta apetite', 'constipacao', 'diarreia', 'manchas', 'abdomen doloroso'],
            'peso_forte': ['febre alta', 'dor abdominal', 'manchas'],
            'chronic_weight': 1.2
        },
        'Tuberculose': {
            'keywords': ['tosse persistente', 'tosse', 'febre', 'suor noturno', 'perda peso', 'fadiga', 'dor peito', 'tosse sangue', 'expectoração'],
            'peso_forte': ['tosse persistente', 'tosse sangue', 'suor noturno', 'perda peso'],
            'chronic_weight': 1.3
        },
        'Dengue': {
            'keywords': ['febre alta', 'dor atras olhos', 'dores musculares', 'dores articulares', 'manchas vermelhas', 'nausea', 'vomito', 'prostracao'],
            'peso_forte': ['dor atras olhos', 'manchas vermelhas', 'dores articulares'],
            'chronic_weight': 1.0
        },
        'Gripe': {
            'keywords': ['febre', 'tosse', 'dor garganta', 'congestão nasal', 'dor cabeça', 'dores musculares', 'fadiga', 'espirros'],
            'peso_forte': ['dor garganta', 'congestão nasal', 'espirros'],
            'chronic_weight': 0.8
        }
    }
    
    # Calcular pontuação para cada doença
    scores = {}
    for disease, data in disease_keywords.items():
        # Pontuação base (cada sintoma conta 1)
        base_score = 0
        for keyword in data['keywords']:
            if keyword in symptoms_lower:
                base_score += 1
        
        # Pontuação extra para sintomas fortes
        strong_score = 0
        for keyword in data['peso_forte']:
            if keyword in symptoms_lower:
                strong_score += 2  # Sintoma forte vale o dobro
        
        total_score = base_score + strong_score
        max_possible = len(data['keywords']) + (len(data['peso_forte']) * 2)
        
        # Calcular percentagem
        percent = (total_score / max_possible) * 100
        
        # Se tiver pelo menos um sintoma, mostrar
        if total_score > 0:
            scores[disease] = round(percent, 1)
    
    # Se não houver sintomas correspondentes, mostrar opções base
    if not scores:
        scores = {
            'Malária': 15.0,
            'Gripe': 15.0,
            'Febre Tifoide': 10.0
        }
    
    # Ordenar por pontuação
    sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # NOVO: Guardar informações do histórico usado
    historico_info = {
        'usado': False,
        'condicoes_encontradas': [],
        'diagnosticos_anteriores': [],
        'ajustes_aplicados': []
    }
    
    # Buscar histórico do paciente
    if patient_id:
        try:
            summary = generate_clinical_summary(patient_id)
            
            # Verificar condições crónicas
            for condition in summary['chronic_conditions']:
                condition_name = condition['condition'].lower()
                historico_info['condicoes_encontradas'].append({
                    'nome': condition['condition'],
                    'data': condition['date'].strftime('%d/%m/%Y') if hasattr(condition['date'], 'strftime') else str(condition['date'])[:10]
                })
                
                if 'malária' in condition_name or 'malaria' in condition_name:
                    if 'Malária' in scores:
                        old_score = scores['Malária']
                        scores['Malária'] = min(98, scores['Malária'] * 1.5)
                        historico_info['ajustes_aplicados'].append(f"Malária: {old_score}% → {scores['Malária']}% (histórico de Malária)")
                        sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                
                elif 'tuberculose' in condition_name or 'tb' in condition_name:
                    if 'Tuberculose' in scores:
                        old_score = scores['Tuberculose']
                        scores['Tuberculose'] = min(98, scores['Tuberculose'] * 1.4)
                        historico_info['ajustes_aplicados'].append(f"Tuberculose: {old_score}% → {scores['Tuberculose']}% (histórico de Tuberculose)")
                        sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            # Verificar diagnósticos anteriores (últimos 3)
            for diag in summary['diagnoses'][-3:]:
                historico_info['diagnosticos_anteriores'].append({
                    'diagnostico': diag['diagnosis'],
                    'data': diag['date'].strftime('%d/%m/%Y') if hasattr(diag['date'], 'strftime') else str(diag['date'])[:10]
                })
            
            if historico_info['condicoes_encontradas'] or historico_info['diagnosticos_anteriores']:
                historico_info['usado'] = True
                
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    # Buscar histórico do paciente para ajustar
    patient_context = ""
    if patient_id:
        try:
            summary = generate_clinical_summary(patient_id)
            
            if summary['chronic_conditions']:
                for condition in summary['chronic_conditions']:
                    condition_name = condition['condition'].lower()
                    if 'malária' in condition_name or 'malaria' in condition_name:
                        if 'Malária' in scores:
                            scores['Malária'] = min(98, scores['Malária'] * 1.5)
                            sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                            patient_context += "Histórico de Malária detectado - probabilidade aumentada. "
                    elif 'tuberculose' in condition_name or 'tb' in condition_name:
                        if 'Tuberculose' in scores:
                            scores['Tuberculose'] = min(98, scores['Tuberculose'] * 1.4)
                            sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                            patient_context += "Histórico de Tuberculose detectado - probabilidade aumentada. "
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    # Gerar alertas
    alerts = []
    if patient_context:
        alerts.append(f"📋 {patient_context}")
    
    top_disease = sorted_diseases[0][0] if sorted_diseases else "Indeterminado"
    
    if top_disease == 'Malária' and scores.get('Malária', 0) > 30:
        alerts.append("⚠️ Risco de Malária - realizar teste rápido")
    elif top_disease == 'Febre Tifoide' and scores.get('Febre Tifoide', 0) > 30:
        alerts.append("⚠️ Suspeita de Febre Tifoide - considerar hemocultura")
    elif top_disease == 'Tuberculose' and scores.get('Tuberculose', 0) > 30:
        alerts.append("⚠️ Possível Tuberculose - solicitar raio-x de tórax")
    
    # Sugerir exames
    exames_sugeridos = ["Hemograma completo"]
    if 'Malária' in scores and scores['Malária'] > 20:
        exames_sugeridos.append("Teste rápido de Malária (TRM)")
    if 'Febre Tifoide' in scores and scores['Febre Tifoide'] > 20:
        exames_sugeridos.append("Hemocultura")
    if 'Tuberculose' in scores and scores['Tuberculose'] > 20:
        exames_sugeridos.append("Raio-X de tórax")
    if 'Dengue' in scores and scores['Dengue'] > 20:
        exames_sugeridos.append("Sorologia para Dengue")
    
    return {
        'possibilidades': [{"doenca": d, "probabilidade": p} for d, p in sorted_diseases[:4]],
        'alertas': alerts,
        'exames_sugeridos': exames_sugeridos,
        'usou_historico': patient_id is not None,
        'historico_info': historico_info
    }


def has_chronic_disease(patient_id, disease_name):
    """Verificar se paciente tem doença crónica no histórico"""
    from app.models.medical_history import MedicalHistory
    
    # Mapeamento de doenças para condições crónicas
    chronic_map = {
        'Malária': ['malária', 'malaria', 'paludismo'],
        'Tuberculose': ['tuberculose', 'tb'],
        'Hipertensão': ['hipertensão', 'hipertensao', 'hta'],
        'Diabetes': ['diabetes', 'dm']
    }
    
    keywords = chronic_map.get(disease_name, [disease_name.lower()])
    
    count = MedicalHistory.query.filter(
        MedicalHistory.patient_id == patient_id,
        MedicalHistory.condition.ilike(f'%{keywords[0]}%')
    ).count()
    
    return count > 0


def simulate_ai_analysis(symptoms_text, patient_history=None):
    """Fallback: IA simulada"""
    
    diseases = {
        "Malária": ["febre", "dor de cabeça", "calafrios", "suor", "nausea"],
        "Febre Tifoide": ["febre alta", "dor abdominal", "dor de cabeça", "falta de apetite", "diarreia"],
        "Tuberculose": ["tosse persistente", "febre", "suor noturno", "perda de peso", "tosse com sangue"],
        "Dengue": ["febre alta", "dor atrás dos olhos", "dores musculares", "manchas vermelhas", "nausea"],
        "Gripe": ["febre", "tosse", "dor de garganta", "congestão nasal", "fadiga"]
    }
    
    symptom_list = symptoms_text.lower()
    probabilities = {}
    
    for disease, keywords in diseases.items():
        matches = sum(1 for keyword in keywords if keyword in symptom_list)
        probability = (matches / len(keywords)) * 100
        if probability > 0:
            probabilities[disease] = round(probability, 1)
    
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    
    alerts = []
    if "Malária" in probabilities and probabilities["Malária"] > 50:
        alerts.append("⚠️ Risco elevado de Malária - considerar teste rápido")
    
    return {
        'possibilidades': [{"doenca": d, "probabilidade": p} for d, p in sorted_probs[:3]],
        'alertas': alerts,
        'exames_sugeridos': ["Hemograma", "Teste rápido de Malária"] if "Malária" in probabilities else ["Avaliação clínica"]
    }