from flask_login import current_user
from flask import session
from datetime import date

def is_generation_allowed():
    if current_user.is_authenticated and current_user.is_admin:
        return True  # админ — всегда можно
    if current_user.is_authenticated:
        return True  # зарегистрированный — всегда можно

    # если не авторизован — гость
    if 'guest_gen_count' not in session or session.get('gen_date') != str(date.today()):
        session['guest_gen_count'] = 0
        session['gen_date'] = str(date.today())

    if session['guest_gen_count'] >= 5:
        return False

    session['guest_gen_count'] += 1
    return True


def is_chat_allowed():
    if current_user.is_authenticated:
        return True
    return not session.get('chat_used_today')


def is_interactive_allowed():
    if current_user.is_authenticated and current_user.is_admin:
        return True
    if current_user.is_authenticated:
        return True

    if 'guest_interact_count' not in session or session.get('gen_date') != str(date.today()):
        session['guest_interact_count'] = 0
        session['gen_date'] = str(date.today())

    if session['guest_interact_count'] >= 5:
        return False

    session['guest_interact_count'] += 1
    return True
