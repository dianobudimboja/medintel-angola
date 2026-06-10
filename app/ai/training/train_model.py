import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
import os

def train_lightweight_model():
    """Treinar modelo leve para diagnóstico"""
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'training_data.csv')
    model_dir = os.path.join(base_dir, 'models')
    
    if not os.path.exists(data_path):
        print(f"Erro: Ficheiro não encontrado")
        return None, None
    
    df = pd.read_csv(data_path)
    
    X = df.drop('doenca', axis=1)
    y = df['doenca']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(le, os.path.join(model_dir, 'label_encoder.joblib'), compress=3)
    
    # Modelo mais leve (menos árvores)
    model = RandomForestClassifier(
        n_estimators=50,      # Reduzido de 100 para 50
        max_depth=8,          # Reduzido de 10 para 8
        random_state=42,
        n_jobs=1              # Single thread para evitar problemas
    )
    
    model.fit(X, y_encoded)
    
    # Avaliar
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Acurácia: {accuracy * 100:.2f}%")
    
    # Salvar modelo comprimido
    joblib.dump(model, os.path.join(model_dir, 'disease_model.joblib'), compress=3)
    print(f"💾 Modelo Guardado (comprimido)")
    
    return model, le

if __name__ == "__main__":
    train_lightweight_model()