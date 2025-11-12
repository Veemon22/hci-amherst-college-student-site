# utils.py
from flask import session, redirect, url_for
from models import User
from functools import wraps

def get_current_user():
    user_id = session.get('user_id')
    return User.query.get(user_id) if user_id else None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g
        user = get_current_user()
        if not user:
            return redirect(url_for('signin'))
        g.user = user
        return f(*args, **kwargs)
    return decorated_function
