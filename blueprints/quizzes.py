from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import session
from flask import url_for
from models import User
from quiz_data import quizzes

quiz_bp = Blueprint('quizzes', __name__, template_folder='../templates')

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


# Quizes Page
@quiz_bp.route("/quizzes")
def quizzes_page():
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))
    return render_template("quizzes.html", username=user.username, quizzes=quizzes)


@quiz_bp.route("/quiz/<quiz_id>")
def quiz_page(quiz_id):
    user = get_current_user()
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('signin'))
    quiz = quizzes.get(quiz_id)

    if not quiz:
        return "Quiz not found", 404

    return render_template("quiz.html", username=user.username, quiz=quiz)
