from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date
from models import db, User

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/auth', methods=['GET', 'POST'])
def auth():
    mode = request.args.get('mode', 'login')
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if request.form['action'] == 'register':
            if User.query.filter_by(email=email).first():
                error = "Пользователь уже существует"
            else:
                is_admin = email == "karina.galimova.98@mail.ru"
                new_user = User(email=email, password=password, is_admin=is_admin)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('auth.auth', mode='login'))
        else:
            user = User.query.filter_by(email=email, password=password).first()
            if user:
                login_user(user)
                session.permanent = True
                return redirect(url_for('dashboard.dashboard'))
            else:
                error = "Неверный email или пароль"

    return render_template('auth.html', mode=mode, error=error)


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.auth', mode='login'))


@auth_blueprint.route('/admin-users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return "Нет доступа"
    users = User.query.all()
    return render_template('admin_users.html', users=users)
