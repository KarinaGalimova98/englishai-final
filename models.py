from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timezone
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    registration_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    tasks_today = db.Column(db.Integer, default=0)
    gpt_today = db.Column(db.Integer, default=0)
    chatbot_today = db.Column(db.Integer, default=0)
    last_reset = db.Column(db.Date, default=date.today)
    is_admin = db.Column(db.Boolean, default=False)
