# Imports List
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
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from models import db
from models import Event
from models import User
from quiz_data import quizzes

import calendar as Calendar
import json
import os
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# Calendar Page
@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))

    # -------------------------
    # Handle Guest Event Form
    # -------------------------
    if request.method == 'POST' and request.form.get('action') == 'add_guest_event':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        sync_to_gcal = request.form.get('sync_to_gcal')

        if title and date_str and time_str:
            datetime_str = f"{date_str}T{time_str}"
            event_date = datetime.fromisoformat(datetime_str)

            # Save locally first
            new_event = Event(
                title=title,
                description=description,
                date=event_date,
                user_id=user.id
            )
            db.session.add(new_event)
            db.session.commit()

            # If syncing to Google Calendar
            if sync_to_gcal and 'gcal_credentials' in session:
                creds_data = session['gcal_credentials']
                creds = Credentials(**creds_data)
                service = build('calendar', 'v3', credentials=creds)

                gcal_event = {
                    'summary': title,
                    'description': description,
                    'start': {'dateTime': event_date.isoformat(), 'timeZone': 'America/New_York'},
                    'end': {'dateTime': (event_date).isoformat(), 'timeZone': 'America/New_York'}
                }

                created_event = service.events().insert(calendarId='primary', body=gcal_event).execute()

                # Save the Google Calendar event ID to local DB
                new_event.gcal_id = created_event.get('id')
                db.session.commit()

                # Update stored credentials if token refreshed
                session['gcal_credentials'] = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }

        return redirect(url_for('calendar'))

    # -------------------------
    # Fetch Local (Guest) Events
    # -------------------------
    now = datetime.now()
    month = int(request.args.get('month', now.month))
    year = int(request.args.get('year', now.year))

    cal = Calendar.Calendar(firstweekday=6)  # Sunday start
    month_days = cal.monthdayscalendar(year, month)

    guest_events = Event.query.filter(
        Event.user_id == user.id,
        Event.date.between(datetime(year, 1, 1), datetime(year, 12, 31))
    ).all()

    # -------------------------
    # Fetch Google Calendar Events
    # -------------------------
    if 'gcal_credentials' in session:
        creds_data = session['gcal_credentials']
        creds = Credentials(**creds_data)
        service = build('calendar', 'v3', credentials=creds)

        now_utc = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            maxResults=50,
            singleEvents=True,
            orderBy='startTime',
            timeMin=now_utc
        ).execute()
        gcal_events_raw = events_result.get('items', [])

        # Build a set of current Google Calendar IDs
        current_gcal_ids = {e['id'] for e in gcal_events_raw}

        # Clear gcal_id from local guest events if deleted in GCal
        for e in guest_events:
            if e.gcal_id and e.gcal_id not in current_gcal_ids:
                e.gcal_id = None
        db.session.commit()

        # Filter out Google Calendar events that are already linked to local guest events
        linked_gcal_ids = {e.gcal_id for e in guest_events if e.gcal_id}
        filtered_gcal_events = [
            e for e in gcal_events_raw
            if e.get('id') not in linked_gcal_ids
        ]

        # Convert Google event start times to datetime objects
        for e in filtered_gcal_events:
            start_str = e.get('start', {}).get('dateTime') or e.get('start', {}).get('date')
            if start_str:
                try:
                    e['start_dt'] = parser.isoparse(start_str)
                except Exception:
                    e['start_dt'] = None
            else:
                e['start_dt'] = None

        gcal_events = filtered_gcal_events

    # -------------------------
    # Month Navigation
    # -------------------------
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    # -------------------------
    # Render Page
    # -------------------------
    return render_template(
        'calendar.html',
        username=user.username,
        calendar_data=month_days,
        current_day=now.day if (month == now.month and year == now.year) else 0,
        current_month=month,
        current_year=year,
        guest_events=guest_events,
        gcal_events=gcal_events,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year
    )

# Authorization route
@app.route('/authorize_gcal')
def authorize_gcal():
    flow = Flow.from_client_config(
        json.loads(cred_json),
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['oauth_state'] = state
    return redirect(authorization_url)

# OAuth2 callback route
@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_config(
        json.loads(cred_json),
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    session['gcal_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return redirect(url_for('calendar'))

@app.route('/disconnect_gcal')
def disconnect_gcal():
    session.pop('gcal_credentials', None)
    return redirect(url_for('calendar'))

@app.route('/sync_all_to_gcal', methods=['POST'])
def sync_all_to_gcal():
    user = get_current_user()
    if not user or 'gcal_credentials' not in session:
        return redirect(url_for('calendar'))

    creds_data = session['gcal_credentials']
    creds = Credentials(**creds_data)
    service = build('calendar', 'v3', credentials=creds)

    # Fetch all guest events for this user that have not been synced yet
    unsynced_events = Event.query.filter_by(user_id=user.id, gcal_id=None).all()

    for event in unsynced_events:
        try:
            gcal_event = {
                'summary': event.title,
                'description': event.description,
                'start': {'dateTime': event.date.isoformat(), 'timeZone': 'America/New_York'},
                'end': {'dateTime': event.date.isoformat(), 'timeZone': 'America/New_York'}
            }

            created_event = service.events().insert(calendarId='primary', body=gcal_event).execute()

            # Store the Google Calendar event ID in the local DB
            event.gcal_id = created_event.get('id')
            db.session.commit()

        except Exception as e:
            print(f"Error syncing event '{event.title}': {e}")

    # Update credentials in case the token was refreshed
    session['gcal_credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    return redirect(url_for('calendar'))

@app.route('/delete_event', methods=['POST'])
def delete_event():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    event_id = request.form.get('event_id')
    gcal_id = request.form.get('gcal_id')

    # Delete local guest event
    if event_id:
        event = Event.query.filter_by(id=event_id, user_id=user.id).first()
        if event:
            # If it has a GCal ID, also delete from GCal
            if gcal_id and 'gcal_credentials' in session:
                creds_data = session['gcal_credentials']
                creds = Credentials(**creds_data)
                service = build('calendar', 'v3', credentials=creds)
                try:
                    service.events().delete(calendarId='primary', eventId=gcal_id).execute()
                except Exception as e:
                    print(f"Error deleting GCal event: {e}")
            db.session.delete(event)
            db.session.commit()

    # Delete standalone GCal event (not in local DB)
    elif gcal_id and 'gcal_credentials' in session:
        creds_data = session['gcal_credentials']
        creds = Credentials(**creds_data)
        service = build('calendar', 'v3', credentials=creds)
        try:
            service.events().delete(calendarId='primary', eventId=gcal_id).execute()
        except Exception as e:
            print(f"Error deleting GCal event: {e}")

    return redirect(url_for('calendar'))

# Quizes Page
@app.route("/quizzes")
def quizzes_page():
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))
    return render_template("quizzes.html", username=user.username, quizzes=quizzes)


@app.route("/quiz/<quiz_id>")
def quiz_page(quiz_id):
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))
    quiz = quizzes.get(quiz_id)

    if not quiz:
        return "Quiz not found", 404

    return render_template("quiz.html", username=user.username, quiz=quiz)

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