# Imports List
from blueprints.calendar import calendar_bp
from blueprints.quizzes import quiz_bp
from datetime import datetime
from dateutil import parser
from dotenv import load_dotenv
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import session
from models import db
from models import User
from quiz_data import quizzes

import json
import os
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(calendar_bp)
app.register_blueprint(quiz_bp)

load_dotenv()
cred_json = os.getenv('GOOGLE_CREDENTIALS')

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

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

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

# Sign Up Page
@app.route('/')
@app.route('/signin', methods=['GET'])
def signin():
    #Redirect to home if already signed in
    user = get_current_user()
    if user:
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
        number = random.randint(1, 999)
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
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))
    return render_template('home.html', username=user.username)

# Dining Page
@app.route('/dining')
def dining():
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))
    return render_template('dining.html', username=user.username)

# About Page
@app.route('/about')
def about():
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))
    return render_template('about.html', username=user.username)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))