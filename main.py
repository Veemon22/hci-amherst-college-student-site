# Imports List
from datetime import datetime
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
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

# Signout Functionality
@app.route('/signout')
def signout():
    session.pop('user_id', None)
    return redirect(url_for('signin'))
