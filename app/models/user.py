from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    reference = db.Column(db.Integer, unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, reference, is_admin):
         self.username = username
         self.password = password
         self.created_at = datetime.utcnow()
         self.expires_at = datetime.utcnow() + timedelta(days=1)
         self.reference = reference
         self.is_admin = is_admin