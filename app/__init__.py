from flask import Flask, render_template
from .config import Config
from .extensions.db import db
from .extensions.auth import login_manager
from flask_migrate import Migrate
from app.services.notification_service import get_user_notifications


def create_app():
    app = Flask(__name__)

    # Configurações
    app.config.from_object(Config)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Inicializar Migrate
    Migrate(app, db)
    
    # Importar Modelos
    from app import models

    # Registar rotas (blueprints depois)
    from .routes.auth_routes import auth_bp
    from .routes.patient_routes import patient_bp
    from .routes.main_routes import main_bp
    from .routes.consultation_routes import consultation_bp
    from .routes.exam_routes import exam_bp
    from .routes.profile_routes import profile_bp
    from .routes.report_routes import report_bp
    from .routes.admin_routes import admin_bp
    
    app.register_blueprint(consultation_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)
    
    from app.models.user import User

    # Saber quem está logado
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Rollback em caso de erro de BD
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('errors/401.html'), 401

    @app.context_processor
    def utility_processor():
        from app.services.admin_service import get_pending_verification_requests
        from app.services.notification_service import get_unread_count, get_user_notifications
        from flask_login import current_user
        
        pending_count = 0
        unread_notifications = 0
        recent_notifications = []
        
        if current_user.is_authenticated:
            if current_user.is_admin():
                pending_count = len(get_pending_verification_requests())
                unread_notifications = get_unread_count(current_user.id)
                recent_notifications = get_user_notifications(current_user.id, 5)
        
        return dict(
            pending_notifications=pending_count,
            unread_notifications=unread_notifications,
            get_recent_notifications=lambda user_id, limit: get_user_notifications(user_id, limit)
        )

    return app