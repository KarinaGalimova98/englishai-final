from flask import Flask
from taskgen import task_blueprint
from chatbot import chat_blueprint  
from interactive_taskgen import interactive_blueprint
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from auth import auth_blueprint
from models import db, User
from dashboard import dashboard_blueprint





app = Flask(__name__)
app.secret_key = "very_secret_key_123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'



db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.auth'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(task_blueprint)
app.register_blueprint(chat_blueprint)
app.register_blueprint(interactive_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(dashboard_blueprint)

with app.app_context():
    db.create_all()

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
app.config['SESSION_PERMANENT'] = True

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)