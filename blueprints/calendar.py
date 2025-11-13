import os
import json
import pytz
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from dateutil import parser
import calendar as Calendar

from flask import Blueprint, render_template, redirect, url_for, request, session
from models import db, Event
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from utils import get_current_user, login_required

calendar_bp = Blueprint('calendar', __name__, template_folder='../templates')

FERNET_KEY = os.getenv('FERNET_KEY')
fernet = Fernet(FERNET_KEY.encode())
cred_json = os.getenv('GOOGLE_CREDENTIALS')
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# ---------- Helper Functions ----------
def get_gcal_credentials():
    """Retrieve and decrypt Google credentials from session."""
    if 'gcal_credentials' not in session:
        return None
    try:
        decrypted = fernet.decrypt(session['gcal_credentials'].encode()).decode()
        creds_data = json.loads(decrypted)
        return Credentials(**creds_data)
    except Exception as e:
        print(f"Error decrypting Google credentials: {e}")
        session.pop('gcal_credentials', None)
        return None


def save_gcal_credentials(creds):
    """Encrypt and save Google credentials back into session."""
    creds_json = json.dumps({
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    })
    session['gcal_credentials'] = fernet.encrypt(creds_json.encode()).decode()


# ---------- Calendar Page ----------
@calendar_bp.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    user = get_current_user()
    eastern = pytz.timezone('America/New_York')

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
            naive_dt = datetime.fromisoformat(f"{date_str}T{time_str}")
            event_date = eastern.localize(naive_dt)
            new_event = Event(title=title, description=description, date=event_date, user_id=user.id)
            db.session.add(new_event)
            db.session.commit()

            # Sync to Google Calendar if selected
            if sync_to_gcal and 'gcal_credentials' in session:
                creds_data = fernet.decrypt(session['gcal_credentials'].encode()).decode()
                creds = Credentials(**json.loads(creds_data))
                service = build('calendar', 'v3', credentials=creds)

                gcal_event = {
                    'summary': title,
                    'description': description,
                    'start': {'dateTime': event_date.isoformat(), 'timeZone': 'America/New_York'},
                    'end': {'dateTime': event_date.isoformat(), 'timeZone': 'America/New_York'}
                }
                created_event = service.events().insert(calendarId='primary', body=gcal_event).execute()
                new_event.gcal_id = created_event.get('id')
                db.session.commit()

                # Re-encrypt credentials
                creds_json = json.dumps({
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                })
                session['gcal_credentials'] = fernet.encrypt(creds_json.encode()).decode()

        return redirect(url_for('calendar.calendar'))

    # -------------------------
    # Determine Month & Year
    # -------------------------
    now = datetime.now(eastern)
    month = int(request.args.get('month', now.month))
    year = int(request.args.get('year', now.year))

    cal = Calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    # -------------------------
    # Month Boundaries (timezone-aware)
    # -------------------------
    month_start = eastern.localize(datetime(year, month, 1))
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    month_end = eastern.localize(datetime(next_year, next_month, 1))

    # -------------------------
    # Local Guest Events
    # -------------------------
    guest_events = Event.query.filter(
        Event.user_id == user.id,
        Event.date >= month_start,
        Event.date < month_end
    ).all()

    # -------------------------
    # Google Calendar Events
    # -------------------------
    gcal_events = []
    if 'gcal_credentials' in session:
        creds_data = fernet.decrypt(session['gcal_credentials'].encode()).decode()
        creds = Credentials(**json.loads(creds_data))
        service = build('calendar', 'v3', credentials=creds)

        time_min = (month_start - timedelta(days=1)).isoformat()
        time_max = (month_end + timedelta(days=1)).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            singleEvents=True,
            orderBy='startTime',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=250
        ).execute()

        gcal_events_raw = events_result.get('items', [])
        current_gcal_ids = {e['id'] for e in gcal_events_raw}

        # Remove deleted links
        for e in guest_events:
            if e.gcal_id and e.gcal_id not in current_gcal_ids:
                e.gcal_id = None
        db.session.commit()

        # Filter out locally linked events
        linked_gcal_ids = {e.gcal_id for e in guest_events if e.gcal_id}
        filtered_gcal_events = [e for e in gcal_events_raw if e.get('id') not in linked_gcal_ids]

        expanded_events = []

        for e in filtered_gcal_events:
            start_info = e.get('start', {})
            end_info = e.get('end', {})
            start_str = start_info.get('dateTime') or start_info.get('date')
            end_str = end_info.get('dateTime') or end_info.get('date')
            if not start_str:
                continue

            try:
                start_dt = parser.isoparse(start_str)
                end_dt = parser.isoparse(end_str) if end_str else start_dt
                if start_dt.tzinfo is None:
                    start_dt = eastern.localize(start_dt)
                if end_dt.tzinfo is None:
                    end_dt = eastern.localize(end_dt)
            except Exception:
                continue

            is_all_day = 'date' in start_info
            if is_all_day:
                start_dt = start_dt.replace(hour=0, minute=0, second=0)
                end_dt = end_dt.replace(hour=0, minute=0, second=0)

            if start_dt >= month_end or end_dt < month_start:
                continue

            if is_all_day or (end_dt - start_dt).days >= 1:
                current_day = start_dt
                while current_day < end_dt:
                    if month_start <= current_day < month_end:
                        clone = e.copy()
                        clone['start_dt'] = current_day
                        clone['is_all_day'] = True
                        expanded_events.append(clone)
                    current_day += timedelta(days=1)
            else:
                e['start_dt'] = start_dt
                e['is_all_day'] = False
                expanded_events.append(e)

        gcal_events = expanded_events

    # -------------------------
    # Month Navigation
    # -------------------------
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1

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

# ---------- Authorization & OAuth ----------
@calendar_bp.route('/authorize_gcal')
@login_required
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


@calendar_bp.route('/oauth2callback')
@login_required
def oauth2callback():
    flow = Flow.from_client_config(
        json.loads(cred_json),
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    save_gcal_credentials(credentials)
    return redirect(url_for('calendar.calendar'))


@calendar_bp.route('/disconnect_gcal')
@login_required
def disconnect_gcal():
    session.pop('gcal_credentials', None)
    return redirect(url_for('calendar.calendar'))


# ---------- Event Management ----------
@calendar_bp.route('/sync_all_to_gcal', methods=['POST'])
@login_required
def sync_all_to_gcal():
    user = get_current_user()
    creds = get_gcal_credentials()
    if not creds:
        return redirect(url_for('calendar.calendar'))

    service = build('calendar', 'v3', credentials=creds)
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
            event.gcal_id = created_event.get('id')
            db.session.commit()
        except Exception as e:
            print(f"Error syncing event '{event.title}': {e}")

    save_gcal_credentials(creds)
    return redirect(url_for('calendar.calendar'))


@calendar_bp.route('/edit_event', methods=['POST'])
@login_required
def edit_event():
    user = get_current_user()
    event_id = request.form.get('event_id')
    gcal_id = request.form.get('gcal_id')
    new_title = request.form.get('title')
    new_time = request.form.get('time')
    new_description = request.form.get('description')

    if event_id:
        event = Event.query.filter_by(id=event_id, user_id=user.id).first()
        if event:
            if new_time:
                hours, minutes = map(int, new_time.split(":"))
                event.date = event.date.replace(hour=hours, minute=minutes)
            if new_title:
                event.title = new_title
            if new_description:
                event.description = new_description
            db.session.commit()

    creds = get_gcal_credentials()
    if gcal_id and creds:
        service = build('calendar', 'v3', credentials=creds)
        gcal_event = {}
        if new_title:
            gcal_event['summary'] = new_title
        if new_description:
            gcal_event['description'] = new_description
        if new_time and event_id:
            start_dt = Event.query.get(event_id).date.isoformat()
            gcal_event['start'] = {'dateTime': start_dt, 'timeZone': 'America/New_York'}
            gcal_event['end'] = {'dateTime': start_dt, 'timeZone': 'America/New_York'}
        if gcal_event:
            try:
                service.events().patch(calendarId='primary', eventId=gcal_id, body=gcal_event).execute()
            except Exception as e:
                print(f"Error updating GCal event: {e}")
        save_gcal_credentials(creds)

    return redirect(url_for('calendar.calendar'))


@calendar_bp.route('/import_gcal_to_db', methods=['POST'])
@login_required
def import_gcal_to_db():
    user = get_current_user()
    creds = get_gcal_credentials()
    if not creds:
        return redirect(url_for('calendar.calendar'))

    service = build('calendar', 'v3', credentials=creds)
    now_utc = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        maxResults=250,
        singleEvents=True,
        orderBy='startTime',
        timeMin=now_utc
    ).execute()

    gcal_events_raw = events_result.get('items', [])
    existing_gcal_ids = {e.gcal_id for e in Event.query.filter_by(user_id=user.id).all() if e.gcal_id}

    for e in gcal_events_raw:
        gcal_id = e.get('id')
        if gcal_id in existing_gcal_ids:
            continue
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

    db.session.commit()
    save_gcal_credentials(creds)
    return redirect(url_for('calendar.calendar'))


@calendar_bp.route('/delete_event', methods=['POST'])
@login_required
def delete_event():
    user = get_current_user()
    event_id = request.form.get('event_id')
    gcal_id = request.form.get('gcal_id')

    creds = get_gcal_credentials()
    if event_id:
        event = Event.query.filter_by(id=event_id, user_id=user.id).first()
        if event:
            if gcal_id and creds:
                service = build('calendar', 'v3', credentials=creds)
                try:
                    service.events().delete(calendarId='primary', eventId=gcal_id).execute()
                except Exception as e:
                    print(f"Error deleting GCal event: {e}")
            db.session.delete(event)
            db.session.commit()
    elif gcal_id and creds:
        service = build('calendar', 'v3', credentials=creds)
        try:
            service.events().delete(calendarId='primary', eventId=gcal_id).execute()
        except Exception as e:
            print(f"Error deleting GCal event: {e}")

    if creds:
        save_gcal_credentials(creds)
    return redirect(url_for('calendar.calendar'))
