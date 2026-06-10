import os
import zipfile
import urllib.request
from tqdm import tqdm

def download_dataset():
    """Download do dataset Chest X-Ray (versão reduzida)"""
    
    # URL do dataset (usando dados do Kaggle - versão pequena para teste)
    # Alternativa: usar dados sintéticos locais
    print("⚠️ Para usar modelo real, é necessário baixar o dataset Chest X-Ray do Kaggle")
    print("1. Aceda a: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia")
    print("2. Faça download do dataset")
    print("3. Extraia na pasta app/ai/chest_xray/data/")
    
    # Criar estrutura de pastas
    os.makedirs('app/ai/chest_xray/data/train/NORMAL', exist_ok=True)
    os.makedirs('app/ai/chest_xray/data/train/PNEUMONIA', exist_ok=True)
    os.makedirs('app/ai/chest_xray/data/val/NORMAL', exist_ok=True)
    os.makedirs('app/ai/chest_xray/data/val/PNEUMONIA', exist_ok=True)
    os.makedirs('app/ai/chest_xray/data/test/NORMAL', exist_ok=True)
    os.makedirs('app/ai/chest_xray/data/test/PNEUMONIA', exist_ok=True)
    
    print("✅ Estrutura de pastas criada!")
    print("\n📁 Coloque as imagens nas pastas:")
    print("   - train/NORMAL/ - imagens normais para treino")
    print("   - train/PNEUMONIA/ - imagens com pneumonia para treino")
    print("   - val/NORMAL/ - imagens normais para validação")
    print("   - val/PNEUMONIA/ - imagens com pneumonia para validação")

if __name__ == "__main__":
    download_dataset()