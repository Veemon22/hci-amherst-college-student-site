from flask import Blueprint, render_template, redirect, url_for, request, session
from models import db, User, Event
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from datetime import datetime
from dateutil import parser
import calendar as Calendar
import json
import os


calendar_bp = Blueprint('calendar', __name__, template_folder='../templates')



# Helper
def get_current_user():
    user_id = session.get('user_id')
    return User.query.get(user_id) if user_id else None

cred_json = os.getenv('GOOGLE_CREDENTIALS')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 

# Calendar Page
@calendar_bp.route('/calendar', methods=['GET', 'POST'])
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

        return redirect(url_for('calendar.calendar'))

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
    gcal_events = []
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
@calendar_bp.route('/authorize_gcal')
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
@calendar_bp.route('/oauth2callback')
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

    return redirect(url_for('calendar.calendar'))

@calendar_bp.route('/disconnect_gcal')
def disconnect_gcal():
    session.pop('gcal_credentials', None)
    return redirect(url_for('calendar.calendar'))

@calendar_bp.route('/sync_all_to_gcal', methods=['POST'])
def sync_all_to_gcal():
    user = get_current_user()
    if not user or 'gcal_credentials' not in session:
        return redirect(url_for('calendar.calendar'))

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

    return redirect(url_for('calendar.calendar'))

@calendar_bp.route('/edit_event', methods=['POST'])
def edit_event():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    event_id = request.form.get('event_id')
    gcal_id = request.form.get('gcal_id')
    new_title = request.form.get('title')
    new_time = request.form.get('time')  # in "HH:MM" 24-hour format
    new_description = request.form.get('description')

    if not (event_id or gcal_id):
        return redirect(url_for('calendar.calendar'))

    # Update local guest event if it exists
    if event_id:
        event = Event.query.filter_by(id=event_id, user_id=user.id).first()
        if event:
            # Update time
            if new_time:
                # Combine existing date with new time
                event_date = event.date
                hours, minutes = map(int, new_time.split(":"))
                event.date = event_date.replace(hour=hours, minute=minutes)
            
            # Update title & description
            if new_title:
                event.title = new_title
            if new_description:
                event.description = new_description

            db.session.commit()

    # Update Google Calendar event if it exists and credentials are present
    if gcal_id and 'gcal_credentials' in session:
        creds_data = session['gcal_credentials']
        creds = Credentials(**creds_data)
        service = build('calendar', 'v3', credentials=creds)

        # Prepare updated GCal event data
        gcal_event = {}
        if new_title:
            gcal_event['summary'] = new_title
        if new_description:
            gcal_event['description'] = new_description
        if new_time and event_id:  # only if we have local event date to combine
            event_date = Event.query.get(event_id).date
            start_dt = event_date.isoformat()
            end_dt = event_date.isoformat()  # adjust if your events have duration
            gcal_event['start'] = {'dateTime': start_dt, 'timeZone': 'America/New_York'}
            gcal_event['end'] = {'dateTime': end_dt, 'timeZone': 'America/New_York'}

        if gcal_event:
            try:
                service.events().patch(calendarId='primary', eventId=gcal_id, body=gcal_event).execute()
            except Exception as e:
                print(f"Error updating GCal event: {e}")

        # Update credentials if token refreshed
        session['gcal_credentials'] = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }

    return redirect(url_for('calendar.calendar'))

@calendar_bp.route('/import_gcal_to_db', methods=['POST'])
def import_gcal_to_db():
    user = get_current_user()
    if not user or 'gcal_credentials' not in session:
        return redirect(url_for('calendar.calendar'))

    creds_data = session['gcal_credentials']
    creds = Credentials(**creds_data)
    service = build('calendar', 'v3', credentials=creds)

    # Pull all upcoming events (or you can adjust time range)
    now_utc = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        maxResults=250,  # adjust as needed
        singleEvents=True,
        orderBy='startTime',
        timeMin=now_utc
    ).execute()

    gcal_events_raw = events_result.get('items', [])

    # Pull existing gcal IDs for this user
    existing_gcal_ids = {e.gcal_id for e in Event.query.filter_by(user_id=user.id).all() if e.gcal_id}

    added_count = 0
    for e in gcal_events_raw:
        gcal_id = e.get('id')
        if gcal_id in existing_gcal_ids:
            continue  # skip duplicates

        start_str = e.get('start', {}).get('dateTime') or e.get('start', {}).get('date')
        if not start_str:
            continue
        try:
            start_dt = parser.isoparse(start_str)
        except Exception:
            continue

        new_event = Event(
            title=e.get('summary', 'No Title'),
            description=e.get('description', ''),
            date=start_dt,
            user_id=user.id,
            gcal_id=gcal_id
        )
        db.session.add(new_event)
        added_count += 1

    db.session.commit()

    print(f"Added {added_count} events to the database.")
    return redirect(url_for('calendar.calendar'))


@calendar_bp.route('/delete_event', methods=['POST'])
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

    return redirect(url_for('calendar.calendar'))