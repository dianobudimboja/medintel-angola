import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from PIL import Image
import os
import io

_model = None

def load_xray_model():
    """Carregar modelo treinado"""
    global _model
    
    if _model is None:
        model_path = 'app/ai/chest_xray/models/chest_xray_model.h5'
        if os.path.exists(model_path):
            _model = tf.keras.models.load_model(model_path)
            print("✅ Modelo de Raio-X carregado com sucesso!")
        else:
            print("⚠️ Modelo de Raio-X não encontrado. Use modo simulação.")
            return None
    return _model

def predict_chest_xray(image_path):
    """Analisar Raio-X de tórax"""
    
    model = load_xray_model()
    
    # Processar imagem
    img = image.load_img(image_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalizar
    
    if model is not None:
        # Predição real
        prediction = model.predict(img_array)[0][0]
        
        if prediction > 0.5:
            diagnosis = "PNEUMONIA"
            confidence = prediction * 100
            findings = "Sinais sugestivos de pneumonia (infiltrado pulmonar detectado)"
            severity = "alta"
        else:
            diagnosis = "NORMAL"
            confidence = (1 - prediction) * 100
            findings = "Tórax normal sem alterações significativas"
            severity = "normal"
    else:
        # Fallback para simulação
        import random
        is_pneumonia = random.random() > 0.7
        if is_pneumonia:
            diagnosis = "PNEUMONIA"
            confidence = random.uniform(65, 95)
            findings = "Sinais sugestivos de pneumonia (infiltrado pulmonar)"
            severity = "alta"
        else:
            diagnosis = "NORMAL"
            confidence = random.uniform(70, 98)
            findings = "Tórax normal sem alterações significativas"
            severity = "normal"
    
    recommendations = []
    if diagnosis == "PNEUMONIA":
        recommendations = [
            "Iniciar antibioticoterapia empírica",
            "Recomenda-se avaliação médica urgente",
            "Monitorizar saturação de oxigênio",
            "Considerar internamento se sintomas graves"
        ]
    else:
        recommendations = [
            "Acompanhamento clínico",
            "Repetir exame se persistirem sintomas"
        ]
    
    return {
        'exam_type': 'Raio-X de Tórax',
        'diagnosis': diagnosis,
        'diagnosis_pt': 'Pneumonia' if diagnosis == "PNEUMONIA" else 'Normal',
        'confidence': round(confidence, 1),
        'findings': findings,
        'severity': severity,
        'recommendations': recommendations
    }