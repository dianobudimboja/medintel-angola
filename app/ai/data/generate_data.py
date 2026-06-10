import pandas as pd
import numpy as np
import random
import os

def generate_training_data(samples=5000):
    """Gerar dados sintéticos para treino da IA"""
    
    dados = []
    
    # Sintomas possíveis
    sintomas = {
        'Malária': ['febre', 'dor_de_cabeca', 'calafrios', 'sudorese', 'nausea', 'vomito', 'dores_musculares', 'fadiga'],
        'Febre Tifoide': ['febre_alta', 'dor_abdominal', 'dor_de_cabeca', 'falta_apetite', 'constipacao', 'diarreia', 'manchas_rosadas'],
        'Tuberculose': ['tosse_persistente', 'febre', 'sudorese_noturna', 'perda_peso', 'fadiga', 'dor_peito', 'tosse_com_sangue'],
        'Dengue': ['febre_alta', 'dor_atras_olhos', 'dores_musculares', 'manchas_vermelhas', 'nausea', 'vomito', 'dores_articulares'],
        'Gripe': ['febre', 'tosse', 'dor_garganta', 'congestao_nasal', 'dor_cabeca', 'dores_musculares', 'fadiga']
    }
    
    for i in range(samples):
        # Escolher doença aleatória
        disease = random.choice(list(sintomas.keys()))
        disease_symptoms = sintomas[disease]
        
        # Criar registro de sintomas
        record = {
            'febre': 0,
            'febre_alta': 0,
            'dor_de_cabeca': 0,
            'dor_atras_olhos': 0,
            'calafrios': 0,
            'sudorese': 0,
            'sudorese_noturna': 0,
            'nausea': 0,
            'vomito': 0,
            'dores_musculares': 0,
            'dores_articulares': 0,
            'fadiga': 0,
            'tosse': 0,
            'tosse_persistente': 0,
            'tosse_com_sangue': 0,
            'dor_garganta': 0,
            'congestao_nasal': 0,
            'dor_abdominal': 0,
            'dor_peito': 0,
            'falta_apetite': 0,
            'perda_peso': 0,
            'constipacao': 0,
            'diarreia': 0,
            'manchas_vermelhas': 0,
            'manchas_rosadas': 0,
            'doenca': disease
        }
        
        # Adicionar sintomas com base na doença (com 70-90% de probabilidade)
        for symptom in disease_symptoms:
            if random.random() < 0.8:  # 80% de chance de ter o sintoma
                record[symptom] = 1
        
        # Adicionar sintomas aleatórios (ruído)
        for symptom in record:
            if symptom != 'doenca' and record[symptom] == 0:
                if random.random() < 0.1:  # 10% de chance de sintoma extra
                    record[symptom] = 1
        
        dados.append(record)
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Salvar dados
    os.makedirs('app/ai/data', exist_ok=True)
    df.to_csv('app/ai/data/training_data.csv', index=False)
    
    print(f"Dados gerados: {samples} amostras")
    print(f"Distribuição das Doenças:")
    print(df['doenca'].value_counts())
    
    return df

if __name__ == "__main__":
    generate_training_data(5000)