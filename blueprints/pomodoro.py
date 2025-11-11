from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Pomodoro, Task
from datetime import datetime

pomodoro_bp = Blueprint('pomodoro', __name__, template_folder='../templates')


# -------------------------
# Helper Functions
# -------------------------

def get_current_user():
    user_id = session.get('user_id')
    return User.query.get(user_id) if user_id else None


def create_or_update_user_pomodoro_settings(user, work, short_break, long_break):
    """Updates the user’s default Pomodoro settings."""
    user.pomodoro_work_duration = int(work)
    user.pomodoro_short_break = int(short_break)
    user.pomodoro_long_break = int(long_break)
    db.session.commit()
    flash("Pomodoro settings updated!", "success")


def add_task(user, title, pomodoro_id):
    if title:
        task = Task(user_id=user.id, pomodoro_id=pomodoro_id, title=title)
        db.session.add(task)
        db.session.commit()
        flash("Task added!", "success")


def complete_task(user, task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == user.id:
        task.completed = True
        db.session.commit()
        flash("Task marked as complete!", "success")


def delete_task(user, task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == user.id:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted!", "success")


# -------------------------
# Routes
# -------------------------

# Pomodoro Configuration Form
@pomodoro_bp.route('/pomodoro/form', methods=['GET', 'POST'])
def pomodoro_form():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        work = request.form.get('work', 25)
        short_break = request.form.get('short_break', 5)
        long_break = request.form.get('long_break', 15)

        create_or_update_user_pomodoro_settings(user, work, short_break, long_break)
        return redirect(url_for('pomodoro.pomodoro'))

    # Pre-fill form with existing or default values
    config = {
        'work': user.pomodoro_work_duration,
        'short_break': user.pomodoro_short_break,
        'long_break': user.pomodoro_long_break
    }

    return render_template('pomodoro_form.html', username=user.username, config=config)


# Main Pomodoro Page
@pomodoro_bp.route('/pomodoro', methods=['GET', 'POST'])
def pomodoro():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    # If user has no Pomodoro sessions yet, redirect to form
    current_pomodoro = Pomodoro.query.filter_by(user_id=user.id, completed=False).first()
    if not current_pomodoro:
        # Auto-create a new Pomodoro session with user defaults
        current_pomodoro = Pomodoro(
            user_id=user.id,
            duration_minutes=user.pomodoro_work_duration,
            timer_type='work'
        )
        db.session.add(current_pomodoro)
        db.session.commit()

    # Handle POST actions
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'start_pomodoro':
            if not current_pomodoro.completed:
                flash("Pomodoro started!", "success")

        elif action == 'complete_pomodoro':
            current_pomodoro.completed = True
            current_pomodoro.end_time = datetime.utcnow()
            user.pomodoros_completed += 1
            db.session.commit()
            flash("Pomodoro completed!", "success")

        elif action == 'add_task':
            title = request.form.get('title')
            add_task(user, title, current_pomodoro.id)

        elif action == 'complete_task':
            task_id = request.form.get('task_id')
            complete_task(user, task_id)

        elif action == 'delete_task':
            task_id = request.form.get('task_id')
            delete_task(user, task_id)

        return redirect(url_for('pomodoro.pomodoro'))

    # GET: Render page
    tasks = Task.query.filter_by(user_id=user.id, pomodoro_id=current_pomodoro.id).all()
    config = {
        'work': user.pomodoro_work_duration,
        'short_break': user.pomodoro_short_break,
        'long_break': user.pomodoro_long_break
    }

    return render_template(
        'pomodoro.html',
        username=user.username,
        user=user,
        config=config,
        current_pomodoro=current_pomodoro,
        tasks=tasks
    )
