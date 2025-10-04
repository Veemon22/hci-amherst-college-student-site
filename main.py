from flask import Flask
from flask import render_template

app = Flask(__name__)

# Home Page
@app.route('/')
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
@app.route('/quizes')
def quizes():
    return render_template('quizes.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')
