from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app.extensions.db import db
from app.services.notification_service import create_password_reset_request

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# 📝 REGISTO
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        specialty = request.form.get("specialty")
        hospital = request.form.get("hospital")

        # Se for "Outro", usar o valor do campo outro_hospital
        if hospital == "Outro":
            hospital = request.form.get("outro_hospital")

        # Validações
        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("A palavra-passe deve ter pelo menos 6 caracteres.", "danger")
            return redirect(url_for("auth.register"))

        if not specialty:
            flash("Selecione uma Especialidade.", "danger")
            return redirect(url_for("auth.register"))
        
        if not hospital:
            flash("Selecione ou digite o nome do Hospital.", "danger")
            return redirect(url_for("auth.register"))

        # Verificar se já existe
        if User.query.filter_by(email=email).first():
            flash("Email já Registado.")
            return redirect(url_for("auth.register"))

        # Criar novo utilizador
        user = User(name=name, email=email, specialty=specialty, hospital=hospital)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(f"Registo feito com sucesso, Dr(a). {name}! Faça Login para continuar.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# 🔐 LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Verificar se conta está suspensa
            if not user.is_active:
                flash("⚠️ A sua conta está suspensa. Contacte o Administrador para mais informações.", "danger")
                return redirect(url_for("auth.login"))
            
            # Verificar se está pendente de verificação
            if user.verification_status == 'pending' and not user.is_verified:
                flash("⚠️ A sua conta aguarda verificação. Um Administrador irá analisar os seus Documentos em breve.", "warning")
            
            login_user(user)
            flash(f"Bem-vindo de Volta, Dr(a). {user.name}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Credenciais inválidas. Verifique Email e Palavra-passe.", "danger")
    
    return render_template("auth/login.html")


# 🚪 LOGOUT
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Página para solicitar recuperação de password"""
    from app.models.user import User
    
    admin_contacts = []
    
    if request.method == "POST":
        email = request.form.get("email")
        
        if email:
            # Verificar se o email existe no sistema
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Buscar apenas ADMIN (não incluir SUPER_ADMIN)
                admins = User.query.filter(
                    User.role == 'admin',
                    User.is_active == True
                ).all()
                
                # Criar notificações para todos os admins
                if admins:
                    admin_ids = [admin.id for admin in admins]
                    create_password_reset_request(email, user.name, admin_ids)
                    
                    # Preparar contactos para mostrar ao médico
                    for admin in admins:
                        admin_contacts.append({
                            'name': admin.name,
                            'email': admin.email,
                            'role': 'Administrador'
                        })
                    
                    flash("Solicitação enviada! Os Administradores foram notificados e entrarão em contacto em breve.", "info")
                else:
                    flash("Nenhum Administrador disponível. Contacte o suporte.", "warning")
            else:
                flash("Email não encontrado no sistema. Verifique o email digitado.", "danger")
                return redirect(url_for("auth.forgot_password"))
        
        return render_template("auth/forgot_password.html", admin_contacts=admin_contacts, email_sent=True, user_email=email)
    
    return render_template("auth/forgot_password.html", admin_contacts=[], email_sent=False)