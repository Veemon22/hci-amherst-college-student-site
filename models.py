from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    events = db.relationship('Event', backref='user', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True, cascade="all, delete-orphan")
    pomodoro_work_duration = db.Column(db.Integer, default=25)
    pomodoro_short_break = db.Column(db.Integer, default=5)
    pomodoro_long_break = db.Column(db.Integer, default=15)
    pomodoros_completed = db.Column(db.Integer, default=0)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_all_day = db.Column(db.Boolean, default=False)
    gcal_id = db.Column(db.String(225), nullable=True)  # To store Google Calendar event ID

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quiz_type = db.Column(db.String(50), default='objective') # 'objective' or 'subjective'
    image = db.Column(db.String(225), nullable=True) 
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('QuizResultRange', backref='quiz', lazy=True, cascade="all, delete-orphan")
    attempts = db.relationship('QuizResult', backref='quiz', lazy=True, cascade="all, delete-orphan")
    creator = db.relationship('User', backref='quizzes', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(225), nullable=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    options = db.relationship('Option', backref='question', lazy=True, cascade="all, delete-orphan")

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


class QuizResultRange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    min_points = db.Column(db.Integer, nullable=False)
    max_points = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(225), nullable=True)
    text = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

class Pomodoro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer) 
    timer_type = db.Column(db.String(20), default='work')  # 'work', 'short_break', 'long_break'
    completed = db.Column(db.Boolean, default=False)

    tasks = db.relationship('Task', backref='pomodoro', lazy=True, cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pomodoro_id = db.Column(db.Integer, db.ForeignKey('pomodoro.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    note = db.Column(db.Text, nullable=True)
    estimated_pomodoros = db.Column(db.Integer, default=1)
    completed_pomodoros = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    priority = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref=db.backref('tasks', lazy=True))
