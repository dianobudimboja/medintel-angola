from app.models.notification import Notification
from app.extensions.db import db
from flask_login import current_user
from datetime import datetime

def create_notification(user_id, title, message, notification_type='info', related_url=None, related_id=None):
    """Criar uma nova notificação para um utilizador"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        related_url=related_url,
        related_id=related_id
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def get_user_notifications(user_id, limit=20, unread_only=False):
    """Buscar notificações do utilizador"""
    query = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc())
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    return query.limit(limit).all()

def mark_as_read(notification_id):
    """Marcar notificação como lida"""
    notification = Notification.query.get(notification_id)
    if notification:
        notification.is_read = True
        db.session.commit()
        return True
    return False

def mark_all_as_read(user_id):
    """Marcar todas notificações como lidas"""
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()

def get_unread_count(user_id):
    """Contar notificações não lidas"""
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()

def create_password_reset_request(user_email, user_name, admin_ids):
    """Criar notificações para todos os admins sobre pedido de reset de password"""
    title = "Pedido de Recuperação de Password"
    message = f"O médico {user_name} ({user_email}) solicitou a recuperação da palavra-passe."
    
    for admin_id in admin_ids:
        create_notification(
            user_id=admin_id,
            title=title,
            message=message,
            notification_type='warning',
            related_url=f"/admin/doctors?search={user_email}",
            related_id=admin_id
        )