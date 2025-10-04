# Imports List
from datetime import datetime
from datetime import date
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import session
from models import db
from models import Event
from models import User
from models import QuizResult

import calendar as Calendar
import os
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# Sign Up Page
@app.route('/')
@app.route('/signin', methods=['GET'])
def signin():
    #Redirect to home if already signed in
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    return render_template('signin.html', user_not_found=False)

@app.route('/new_user', methods=['POST'])
def new_user():
    # Pulls all users in DB
    existing_usernames = [u.username for u in User.query.all()]

    # Generate a unique username
    while True:
        adjective = random.choice(adjectives)
        animal = random.choice(animals)
        number = random.randint(1, 99)
        username = f"{adjective}{animal}{number}"
        if username not in existing_usernames:    
            break
    
    # Create new user in DB
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    # Store ID in session
    session['user_id'] = new_user.id

    return redirect(url_for('home'))

#Sigin In Existing User
@app.route('/existing_user', methods=['POST'])
def existing_user():
    username =  request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('home'))
    else:
        return render_template('signin.html', user_not_found=True)

# Signout Functionality
@app.route('/signout')
def signout():
    session.pop('user_id', None)
    return redirect(url_for('signin'))

# Home Page
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    user = User.query.get(session['user_id'])
    return render_template('home.html', username=user.username)

# Dining Page
@app.route('/dining')
def dining():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    user = User.query.get(session['user_id'])
    return render_template('dining.html', username=user.username)

# Calendar Page
@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user = User.query.get(session['user_id'])

    # Handle form submission
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        hour = int(request.form.get('hour', 0))
        minute = int(request.form.get('minute', 0))

        if not title or not date_str:
            # could pass error message back to template
            return redirect(url_for('calendar'))

        event_date = datetime.fromisoformat(date_str)
        event_date = event_date.replace(hour=hour, minute=minute)

        new_event = Event(
            title=title,
            description=description,
            date=event_date,
            user_id=user.id
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('calendar_page'))

    # Build calendar for current month
    now = datetime.now()
    cal = Calendar.Calendar(firstweekday=6)  # Sunday start
    month_days = cal.monthdayscalendar(now.year, now.month)  # full month

    # Get user's events for current month
    events = Event.query.filter_by(user_id=user.id).all()

    return render_template(
        'calendar.html',
        username=user.username,
        calendar_data=month_days,
        current_day=now.day,
        current_month=now.month,
        current_year=now.year,
        events=events
    )
# Quizes Page
@app.route('/quizzes')
def quizzes():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    user = User.query.get(session['user_id'])
    return render_template('quizzes.html', username=user.username)

# About Page
@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    user = User.query.get(session['user_id'])
    return render_template('about.html', username=user.username)

