import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
import os

def train_transfer_learning():
    """Usar VGG16 pré-treinado para transfer learning"""
    
    train_dir = 'app/ai/chest_xray/data/train'
    val_dir = 'app/ai/chest_xray/data/val'
    
    # Data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(150, 150),
        batch_size=32,
        class_mode='binary'
    )
    
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(150, 150),
        batch_size=32,
        class_mode='binary'
    )
    
    # Carregar VGG16 pré-treinado (sem a cabeça)
    base_model = VGG16(
        weights='imagenet',
        include_top=False,
        input_shape=(150, 150, 3)
    )
    
    # Congelar camadas base
    base_model.trainable = False
    
    # Adicionar novas camadas
    model = models.Sequential([
        base_model,
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        loss='binary_crossentropy',
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        metrics=['accuracy']
    )
    
    print("📊 Treinando com Transfer Learning...")
    
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // 32,
        epochs=20,
        validation_data=val_generator,
        validation_steps=val_generator.samples // 32
    )
    
    # Salvar modelo
    os.makedirs('app/ai/chest_xray/models', exist_ok=True)
    model.save('app/ai/chest_xray/models/chest_xray_model.keras')
    
    print("✅ Modelo salvo!")
    
    return model

if __name__ == "__main__":
    train_transfer_learning()