import os

class Config:
    
    SECRET_KEY = os.getenv("SECRET_KEY", "chave_super_secreta")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'dicom', 'dcm'}

    # IA Settings
    USE_TENSORFLOW = False  # Manter False por enquanto
    TENSORFLOW_MODEL_PATH = 'app/ai/chest_xray/models/chest_xray_model.keras'