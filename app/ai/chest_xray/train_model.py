import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import os
import matplotlib.pyplot as plt

def create_improved_model():
    """Criar modelo CNN melhorado com regularização"""
    
    model = models.Sequential([
        # Primeira camada convolucional com regularização
        layers.Conv2D(32, (3, 3), activation='relu', 
                      kernel_regularizer=regularizers.l2(0.001),
                      input_shape=(150, 150, 3)),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Segunda camada
        layers.Conv2D(64, (3, 3), activation='relu',
                      kernel_regularizer=regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Terceira camada
        layers.Conv2D(128, (3, 3), activation='relu',
                      kernel_regularizer=regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Quarta camada
        layers.Conv2D(128, (3, 3), activation='relu',
                      kernel_regularizer=regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Flatten e camadas densas
        layers.Flatten(),
        layers.Dense(256, activation='relu',
                     kernel_regularizer=regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    return model

def train_improved_model():
    """Treinar modelo melhorado"""
    
    train_dir = 'app/ai/chest_xray/data/train'
    val_dir = 'app/ai/chest_xray/data/val'
    
    if not os.path.exists(train_dir):
        print("❌ Dataset não encontrado!")
        print("Execute primeiro: python app/ai/chest_xray/generate_synthetic_data.py")
        return None
    
    # Data augmentation mais agressiva
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Validação apenas com rescale
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Carregar imagens
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(150, 150),
        batch_size=16,  # Batch menor
        class_mode='binary'
    )
    
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(150, 150),
        batch_size=16,
        class_mode='binary'
    )
    
    # Criar modelo melhorado
    model = create_improved_model()
    
    # Compilar com learning rate menor
    model.compile(
        loss='binary_crossentropy',
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        metrics=['accuracy']
    )
    
    print(f"📊 Treino com {train_generator.samples} imagens")
    print(f"📊 Validação com {val_generator.samples} imagens")
    
    # Callbacks para evitar overfitting
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=0.00001
    )
    
    # Treinar com mais épocas mas early stopping
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // 16,
        epochs=50,
        validation_data=val_generator,
        validation_steps=val_generator.samples // 16,
        callbacks=[early_stop, reduce_lr]
    )
    
    # Salvar modelo
    os.makedirs('app/ai/chest_xray/models', exist_ok=True)
    
    # Salvar no formato nativo do Keras
    model.save('app/ai/chest_xray/models/chest_xray_model.keras')
    
    # Converter para H5 também
    model.save('app/ai/chest_xray/models/chest_xray_model.h5')
    
    print("✅ Modelo salvo!")
    
    # Plotar resultados
    plot_training_history(history)
    
    # Avaliação final
    test_loss, test_acc = model.evaluate(val_generator)
    print(f"\n📈 Acurácia na validação: {test_acc*100:.2f}%")
    
    return model, history

def plot_training_history(history):
    """Plotar gráficos"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Acurácia
    ax1.plot(history.history['accuracy'], label='Treino', marker='o')
    ax1.plot(history.history['val_accuracy'], label='Validação', marker='o')
    ax1.set_title('Acurácia do Modelo')
    ax1.set_xlabel('Época')
    ax1.set_ylabel('Acurácia')
    ax1.legend()
    ax1.grid(True)
    
    # Loss
    ax2.plot(history.history['loss'], label='Treino', marker='o')
    ax2.plot(history.history['val_loss'], label='Validação', marker='o')
    ax2.set_title('Loss do Modelo')
    ax2.set_xlabel('Época')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('app/ai/chest_xray/models/training_history.png')
    plt.show()

if __name__ == "__main__":
    train_improved_model()