import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions.db import db

print("🔧 Iniciando criação da base de dados...")

app = create_app()

with app.app_context():
    # Criar todas as tabelas
    db.create_all()
    print("✅ Base de dados criada com sucesso!")
    
    # Verificar tabelas (forma compatível)
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("📊 Tabelas criadas:", tables)
    
    # Criar Super Admin se não existir
    from app.models.user import User
    admin = User.query.filter_by(email="cientificando17@gmail.com").first()
    
    if not admin:
        admin = User(
            name="Super Administrador",
            email="cientificando17@gmail.com",
            role="super_admin",
            is_verified=True,
            is_active=True,
            verification_status='approved',
            specialty="Administração",
            hospital="MedIntel Angola"
        )
        admin.set_password("Admin123456")
        db.session.add(admin)
        db.session.commit()
        print("✅ Super Administrador criado!")
        print("   Email: cientificando17@gmail.com")
        print("   Password: Admin123456")
    else:
        print("⚠️ Super Administrador já existe!")

print("🎉 Setup concluído!")