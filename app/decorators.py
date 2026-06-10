from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator para rotas que só admins podem aceder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para aceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Acesso negado. Apenas administradores.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Decorator para rotas que só Super Admins podem aceder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para aceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.is_super_admin():
            flash('Acesso negado. Apenas Super Administradores.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def verified_doctor_required(f):
    """Decorator para médicos verificados"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para aceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.is_verified_doctor() and not current_user.is_admin():
            flash('A sua conta aguarda verificação por um administrador.', 'warning')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function