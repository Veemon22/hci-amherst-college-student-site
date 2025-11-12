import os
from flask import Blueprint, render_template, redirect, session, url_for, request, current_app, abort
from werkzeug.utils import secure_filename
from models import db, User, Quiz, Question, Option, QuizResultRange, QuizResult
from utils import get_current_user, login_required

quiz_bp = Blueprint('quizzes', __name__, template_folder='../templates')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# ---------- Helpers ----------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder = os.path.join(current_app.root_path, 'static', 'uploads', 'quiz_images')
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return f'uploads/quiz_images/{filename}'
    return None


def can_publish(quiz):
    """Helper to determine if a quiz is valid for publishing"""
    if not quiz.questions or not quiz.results:
        return False
    for q in quiz.questions:
        if len(q.options) < 2 or len(q.options) > 4:
            return False
        if quiz.quiz_type == "objective" and not any(o.is_correct for o in q.options):
            return False
    ranges = [(r.min_points, r.max_points) for r in quiz.results]
    ranges.sort()
    for i in range(len(ranges)-1):
        if ranges[i][1] >= ranges[i+1][0]:
            return False
    return True


# ---------- Quiz Pages ----------
@quiz_bp.route('/quizzes')
@login_required
def quizzes_page():
    user = get_current_user()
    published_quizzes = Quiz.query.filter_by(is_published=True).all()
    user_quizzes = Quiz.query.filter_by(created_by=user.id).all()
    return render_template(
        "quizzes.html",
        username=user.username,
        published_quizzes=published_quizzes,
        user_quizzes=user_quizzes,
        can_publish=can_publish
    )


# ---------- Create / Edit Quiz ----------
def save_questions_and_results(quiz):
    seen_question_ids = set()
    question_idx = 0

    while f"question_text_{question_idx}" in request.form:
        q_text = request.form.get(f"question_text_{question_idx}")
        if not q_text.strip():
            question_idx += 1
            continue

        q_id = request.form.get(f"question_id_{question_idx}")
        question = Question.query.get(int(q_id)) if q_id else Question(quiz_id=quiz.id)
        question.text = q_text

        # Image
        q_file = request.files.get(f"question_image_{question_idx}")
        if q_file:
            q_image_path = save_image(q_file)
            if q_image_path:
                question.image = q_image_path

        db.session.add(question)
        db.session.flush()
        seen_question_ids.add(question.id)

        # Remove old options
        Option.query.filter_by(question_id=question.id).delete()

        option_texts = request.form.getlist(f"option_text_{question_idx}[]")
        option_points = request.form.getlist(f"option_points_{question_idx}[]")
        option_correct = request.form.getlist(f"option_correct_{question_idx}[]")

        for i, text in enumerate(option_texts):
            if not text.strip():
                continue
            points = int(option_points[i]) if option_points[i] else 0
            is_correct = "true" in option_correct[i:i+1]
            db.session.add(Option(text=text, points=points, is_correct=is_correct, question_id=question.id))

        question_idx += 1

    # Remove deleted questions
    for q in quiz.questions:
        if q.id not in seen_question_ids:
            db.session.delete(q)

    # Results
    QuizResultRange.query.filter_by(quiz_id=quiz.id).delete()
    mins = request.form.getlist("result_min[]")
    maxs = request.form.getlist("result_max[]")
    texts = request.form.getlist("result_text[]")

    for mn, mx, txt in zip(mins, maxs, texts):
        if txt.strip():
            db.session.add(QuizResultRange(min_points=int(mn), max_points=int(mx), text=txt, quiz_id=quiz.id))

    db.session.commit()


@quiz_bp.route('/quiz/new', methods=['GET', 'POST'])
@login_required
def create_quiz():
    user = get_current_user()
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        quiz_type = request.form.get("quiz_type", "objective")
        quiz_file = request.files.get("quiz_image")
        image_path = save_image(quiz_file) if quiz_file else None

        quiz = Quiz(title=title, description=description, quiz_type=quiz_type, created_by=user.id)
        if image_path:
            quiz.image = image_path

        db.session.add(quiz)
        db.session.flush()
        save_questions_and_results(quiz)
        return redirect(url_for("quizzes.edit_quiz", quiz_id=quiz.id))

    return render_template("quiz_form.html", quiz=None, username=user.username)


@quiz_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.created_by != user.id:
        abort(403)

    if request.method == "POST":
        quiz.title = request.form.get("title")
        quiz.description = request.form.get("description")
        quiz.quiz_type = request.form.get("quiz_type", "objective")
        quiz_file = request.files.get("quiz_image")
        if quiz_file:
            image_path = save_image(quiz_file)
            if image_path:
                quiz.image = image_path

        save_questions_and_results(quiz)
        return redirect(url_for("quizzes.quizzes_page"))

    return render_template("quiz_form.html", quiz=quiz, username=user.username)


# ---------- Delete / Publish ----------
@quiz_bp.route("/quiz/<int:quiz_id>/delete", methods=["POST"])
@login_required
def delete_quiz(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.created_by != user.id:
        abort(403)

    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('quizzes.quizzes_page'))


@quiz_bp.route("/quiz/<int:quiz_id>/publish", methods=["POST"])
@login_required
def publish_quiz(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.created_by != user.id:
        abort(403)

    if not can_publish(quiz):
        return redirect(url_for('quizzes.quizzes_page'))

    quiz.is_published = True
    db.session.commit()
    return redirect(url_for('quizzes.quizzes_page'))


@quiz_bp.route("/quiz/<int:quiz_id>/unpublish", methods=["POST"])
@login_required
def unpublish_quiz(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.created_by != user.id:
        abort(403)

    quiz.is_published = False
    db.session.commit()
    return redirect(url_for('quizzes.quizzes_page'))


# ---------- Delete Question / Option / Result ----------
@quiz_bp.route("/quiz/question/<int:question_id>/delete", methods=["POST"])
@login_required
def delete_question(question_id):
    user = get_current_user()
    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get(question.quiz_id)
    if quiz.created_by != user.id:
        abort(403)

    db.session.delete(question)
    db.session.commit()
    return '', 204


@quiz_bp.route("/quiz/option/<int:option_id>/delete", methods=["POST"])
@login_required
def delete_option(option_id):
    user = get_current_user()
    option = Option.query.get_or_404(option_id)
    quiz = Quiz.query.get(option.question.quiz_id)
    if quiz.created_by != user.id:
        abort(403)

    db.session.delete(option)
    db.session.commit()
    return '', 204


@quiz_bp.route("/quiz/result/<int:result_id>/delete", methods=["POST"])
@login_required
def delete_result(result_id):
    user = get_current_user()
    result = QuizResultRange.query.get_or_404(result_id)
    quiz = Quiz.query.get(result.quiz_id)
    if quiz.created_by != user.id:
        abort(403)

    db.session.delete(result)
    db.session.commit()
    return '', 204


# ---------- Take / Submit Quiz ----------
@quiz_bp.route("/quiz/<int:quiz_id>/take")
@login_required
def take_quiz(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    if not quiz.is_published:
        abort(403)
    return render_template("quiz.html", quiz=quiz, username=user.username)


@quiz_bp.route("/quiz/<int:quiz_id>/submit", methods=["POST"])
@login_required
def submit_quiz(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)

    data = request.get_json()
    score = data.get("score", 0)
    total = data.get("total", 0)
    result_text = data.get("result_text", "")

    quiz_result = QuizResult(
        score=score,
        total=total,
        text=result_text,
        user_id=user.id,
        quiz_id=quiz.id
    )
    db.session.add(quiz_result)
    db.session.commit()

    return {"message": "Result saved successfully!"}, 200


@quiz_bp.route("/quiz/<int:quiz_id>/results")
@login_required
def view_past_results(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)

    results = (
        QuizResult.query
        .filter_by(user_id=user.id, quiz_id=quiz.id)
        .order_by(QuizResult.timestamp.desc())
        .all()
    )

    return render_template("quiz_results.html", quiz=quiz, results=results, username=user.username)
