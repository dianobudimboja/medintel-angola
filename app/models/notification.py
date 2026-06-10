from app.extensions.db import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notifications"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados da notificação
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, warning, success, danger
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    
    # Destinatário
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Dados relacionados (opcional)
    related_url = db.Column(db.String(300), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    
    # Datas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relação
    user = db.relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"