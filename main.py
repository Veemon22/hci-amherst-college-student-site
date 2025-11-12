# Imports List
from blueprints.calendar import calendar_bp
from blueprints.pomodoro import pomodoro_bp
from blueprints.quizzes import quiz_bp
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, session
from ics import Calendar as ICSCalendar
from models import db, Event, User
from utils import get_current_user, login_required

import os
import random
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'quiz_images')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

app.register_blueprint(calendar_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(pomodoro_bp)

load_dotenv()
cred_json = os.getenv('GOOGLE_CREDENTIALS')

adjectives = [
    "Adventurous", "Brave", "Curious", "Diligent", "Energetic",
    "Friendly", "Generous", "Honest", "Innovative", "Joyful"
]
animals = [
    "Dog", "Cat", "Elephant", "Giraffe", "Kangaroo",
    "Lion", "Panda", "Rabbit", "Tiger", "Zebra"
]

db.init_app(app)
with app.app_context():
    db.create_all()


# ---------- Routes ----------
@app.route('/')
@app.route('/signin', methods=['GET'])
def signin():
    user = get_current_user()
    if user:
        return redirect(url_for('home'))
    return render_template('signin.html', user_not_found=False)


@app.route('/new_user', methods=['POST'])
def new_user():
    existing_usernames = [u.username for u in User.query.all()]

    # Generate unique username
    while True:
        adjective = random.choice(adjectives)
        animal = random.choice(animals)
        number = random.randint(1, 999)
        username = f"{adjective}{animal}{number}"
        if username not in existing_usernames:
            break

    new_user_obj = User(username=username)
    db.session.add(new_user_obj)
    db.session.commit()

    # Import default calendar events
    ics_path = os.path.join(app.root_path, 'calendar_info/calendar_25_26.ics')
    import_ics_for_user(new_user_obj, ics_path)

    session['user_id'] = new_user_obj.id
    return redirect(url_for('home'))


@app.route('/existing_user', methods=['POST'])
def existing_user():
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('home'))
    return render_template('signin.html', user_not_found=True)


@app.route('/signout')
def signout():
    session.pop('user_id', None)
    return redirect(url_for('signin'))


# ---------- ICS Import ----------
def import_ics_for_user(user, ics_path):
    """Imports events from a .ics file for a given user."""
    if not user or not ics_path or not os.path.exists(ics_path):
        return 0

    added_count = 0
    with open(ics_path, 'r') as f:
        ics_calendar = ICSCalendar(f.read())

    for ics_event in ics_calendar.events:
        start_dt = ics_event.begin.datetime

        # Skip duplicates
        exists = Event.query.filter_by(
            user_id=user.id,
            title=ics_event.name,
            date=start_dt
        ).first()
        if exists:
            continue

        new_event = Event(
            title=ics_event.name or "No Title",
            description=ics_event.description or "",
            date=start_dt,
            user_id=user.id
        )
        db.session.add(new_event)
        added_count += 1

    db.session.commit()
    return added_count


# ---------- Protected Pages ----------
@app.route('/home')
@login_required
def home():
    user = get_current_user()
    return render_template('home.html', username=user.username)


@app.route('/dining')
@login_required
def dining():
    user = get_current_user()
    return render_template('dining.html', username=user.username)


@app.route('/about')
@login_required
def about():
    user = get_current_user()
    return render_template('about.html', username=user.username)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
