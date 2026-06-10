import numpy as np
from PIL import Image
import os
import random

def generate_synthetic_xray(width=150, height=150):
    """Gerar imagem sintética de Raio-X"""
    
    # Criar imagem em tons de cinza (simulando Raio-X)
    img_array = np.random.normal(128, 50, (height, width))
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    # Adicionar ruído
    noise = np.random.normal(0, 20, (height, width))
    img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    # Criar padrão de pulmão (simplificado)
    center_y, center_x = height // 2, width // 2
    for y in range(height):
        for x in range(width):
            # Simular pulmão como área mais clara
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance < height // 3:
                img_array[y, x] = min(255, img_array[y, x] + 30)
    
    return Image.fromarray(img_array, mode='L')

def generate_dataset(num_normal=500, num_pneumonia=500):
    """Gerar dataset sintético"""
    
    # Criar pastas
    for split in ['train', 'val', 'test']:
        os.makedirs(f'app/ai/chest_xray/data/{split}/NORMAL', exist_ok=True)
        os.makedirs(f'app/ai/chest_xray/data/{split}/PNEUMONIA', exist_ok=True)
    
    # Gerar imagens normais
    for i in range(num_normal):
        img = generate_synthetic_xray()
        
        # Distribuir entre train/val/test
        if i < num_normal * 0.7:
            img.save(f'app/ai/chest_xray/data/train/NORMAL/normal_{i}.png')
        elif i < num_normal * 0.85:
            img.save(f'app/ai/chest_xray/data/val/NORMAL/normal_{i}.png')
        else:
            img.save(f'app/ai/chest_xray/data/test/NORMAL/normal_{i}.png')
    
    # Gerar imagens com pneumonia (adicionar manchas)
    for i in range(num_pneumonia):
        img = generate_synthetic_xray()
        img_array = np.array(img)
        
        # Adicionar manchas (simulando pneumonia)
        h, w = img_array.shape
        num_spots = random.randint(1, 5)
        for _ in range(num_spots):
            x = random.randint(w//4, 3*w//4)
            y = random.randint(h//4, 3*h//4)
            radius = random.randint(10, 30)
            for dy in range(-radius, radius):
                for dx in range(-radius, radius):
                    if dx*dx + dy*dy < radius*radius:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            img_array[ny, nx] = min(255, img_array[ny, nx] + 80)
        
        img = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
        
        # Distribuir entre train/val/test
        if i < num_pneumonia * 0.7:
            img.save(f'app/ai/chest_xray/data/train/PNEUMONIA/pneumonia_{i}.png')
        elif i < num_pneumonia * 0.85:
            img.save(f'app/ai/chest_xray/data/val/PNEUMONIA/pneumonia_{i}.png')
        else:
            img.save(f'app/ai/chest_xray/data/test/PNEUMONIA/pneumonia_{i}.png')
    
    print(f"✅ Dataset sintético gerado:")
    print(f"   - Normais: {num_normal}")
    print(f"   - Com Pneumonia: {num_pneumonia}")

if __name__ == "__main__":
    # Gerar mais dados para melhor treino
    generate_dataset(num_normal=2000, num_pneumonia=2000)