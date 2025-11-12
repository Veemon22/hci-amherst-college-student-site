from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, Pomodoro, Task
from datetime import datetime
from utils import get_current_user, login_required  # assuming these exist in main.py

pomodoro_bp = Blueprint('pomodoro', __name__, template_folder='../templates')


# ---------- Helper Functions ----------
def create_or_update_user_pomodoro_settings(user, work, short_break, long_break):
    user.pomodoro_work_duration = int(work)
    user.pomodoro_short_break = int(short_break)
    user.pomodoro_long_break = int(long_break)
    db.session.commit()


def add_task(user, title, pomodoro_id, note=None, estimated_pomodoros=1, priority=0):
    if not title:
        return
    task = Task(user_id=user.id, pomodoro_id=pomodoro_id, title=title, completed=False, priority=int(priority))
    if hasattr(Task, 'note') and note:
        task.note = note
    if hasattr(Task, 'estimated_pomodoros') and estimated_pomodoros:
        task.estimated_pomodoros = int(estimated_pomodoros)
    db.session.add(task)
    db.session.commit()


def complete_task(user, task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == user.id:
        task.completed = True
        db.session.commit()


def delete_task(user, task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == user.id:
        db.session.delete(task)
        db.session.commit()


def increment_task_pomodoros(user, pomodoro_id):
    tasks = Task.query.filter_by(user_id=user.id, pomodoro_id=pomodoro_id, completed=False).all()
    for task in tasks:
        task.completed_pomodoros += 1
    db.session.commit()


# ---------- Routes ----------
@pomodoro_bp.route('/pomodoro/form', methods=['GET', 'POST'])
@login_required
def pomodoro_form():
    user = get_current_user()

    if request.method == 'POST':
        work = request.form.get('work', 25)
        short_break = request.form.get('short_break', 5)
        long_break = request.form.get('long_break', 15)
        create_or_update_user_pomodoro_settings(user, work, short_break, long_break)
        return redirect(url_for('pomodoro.pomodoro'))

    config = {
        'work': user.pomodoro_work_duration,
        'short_break': user.pomodoro_short_break,
        'long_break': user.pomodoro_long_break
    }
    return render_template('pomodoro_form.html', username=user.username, config=config)


@pomodoro_bp.route('/pomodoro', methods=['GET', 'POST'])
@login_required
def pomodoro():
    user = get_current_user()

    # Ensure a Pomodoro exists for the user
    current_pomodoro = Pomodoro.query.filter_by(user_id=user.id).first()
    if not current_pomodoro:
        current_pomodoro = Pomodoro(
            user_id=user.id,
            timer_type='work',
            duration_minutes=user.pomodoro_work_duration,
            start_time=datetime.utcnow()
        )
        db.session.add(current_pomodoro)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'start_pomodoro':
            current_pomodoro.start_time = datetime.utcnow()

        elif action == 'complete_pomodoro':
            if current_pomodoro.timer_type == 'work':
                user.pomodoros_completed += 1
                increment_task_pomodoros(user, current_pomodoro.id)
                next_type = 'long_break' if user.pomodoros_completed % 4 == 0 else 'short_break'
                next_duration = user.pomodoro_long_break if next_type == 'long_break' else user.pomodoro_short_break
            else:
                next_type = 'work'
                next_duration = user.pomodoro_work_duration

            current_pomodoro.timer_type = next_type
            current_pomodoro.duration_minutes = next_duration
            current_pomodoro.start_time = datetime.utcnow()
            current_pomodoro.end_time = None
            current_pomodoro.completed = False
            db.session.commit()

        elif action == 'add_task':
            add_task(
                user,
                request.form.get('title'),
                current_pomodoro.id,
                note=request.form.get('note'),
                estimated_pomodoros=request.form.get('estimated_pomodoros', 1),
                priority=request.form.get('priority', 0)
            )

        elif action == 'complete_task':
            complete_task(user, request.form.get('task_id'))

        elif action == 'delete_task':
            delete_task(user, request.form.get('task_id'))

        return redirect(url_for('pomodoro.pomodoro'))

    tasks = Task.query.filter_by(user_id=user.id, pomodoro_id=current_pomodoro.id).all()

    if current_pomodoro.timer_type == 'work':
        duration = user.pomodoro_work_duration
    elif current_pomodoro.timer_type == 'short_break':
        duration = user.pomodoro_short_break
    else:
        duration = user.pomodoro_long_break

    config = {
        'work': user.pomodoro_work_duration,
        'short_break': user.pomodoro_short_break,
        'long_break': user.pomodoro_long_break,
        'current_type': current_pomodoro.timer_type,
        'duration': duration
    }

    return render_template(
        'pomodoro.html',
        username=user.username,
        user=user,
        config=config,
        current_pomodoro=current_pomodoro,
        tasks=tasks
    )
