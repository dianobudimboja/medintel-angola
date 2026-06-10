import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions.db import db
from app.models.user import User

app = create_app()

with app.app_context():
    # Verificar se já existe Super Admin
    super_admin = User.query.filter_by(role='super_admin').first()
    
    if not super_admin:
        admin = User(
            name="CIENTIFICANDO",
            email="cientificando17@gmail.com",
            role="super_admin",
            is_verified=True,
            is_active=True,
            specialty="Administração",
            hospital="MedIntel"
        )
        admin.set_password("Admin123456")
        db.session.add(admin)
        db.session.commit()
        print("Super Administrador criado com sucesso!")
        print("Email: cientificando17@gmail.com")
        print("Password: Admin123456")
    else:
        print("Super Administrador já Existe!")