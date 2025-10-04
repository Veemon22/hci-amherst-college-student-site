# Imports List
from datetime import datetime
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from models import db
from models import Event
from models import User
from models import QuizResult

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
@app.route('/signin')
def signin():
    # Redirect to home if already logged in
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    # Generate a unique username
    while True:
        adjective = random.choice(adjectives)
        animal = random.choice(animals)
        username = f"{adjective}{animal}"
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:    
            break
    
    # Create new user in DB
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    # Store ID in session
    session['user_id'] = new_user.id

    return render_template('signin.html', username=new_user.username)

# Home Page
@app.route('/home')
def home():
    return render_template('home.html')

# Dining Page
@app.route('/dining')
def dining():
    return render_template('dining.html')

# Calender Page
@app.route('/calender')
def calender():
    return render_template('calender.html')

# Quizes Page
@app.route('/quizzes')
def quizes():
    return render_template('quizzes.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')
