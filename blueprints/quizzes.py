from flask import Blueprint, render_template, redirect, session, url_for, request
from models import db, User, Quiz, Question, Option, QuizResultRange

quiz_bp = Blueprint('quizzes', __name__, template_folder='../templates')

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

# List quizzes
@quiz_bp.route('/quizzes')
def quizzes_page():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    published_quizzes = Quiz.query.filter_by(is_published=True).all()
    user_quizzes = Quiz.query.filter_by(created_by=user.id).all()

    return render_template(
        "quizzes.html",
        username=user.username,
        published_quizzes=published_quizzes,
        user_quizzes=user_quizzes
    )

# Create a new quiz
@quiz_bp.route('/quiz/new', methods=['GET', 'POST'])
def create_quiz():
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image = request.form.get('image')
        quiz_type = request.form.get('quiz_type', 'objective')

        new_quiz = Quiz(
            title=title,
            description=description,
            image=image,
            quiz_type=quiz_type,
            is_published=False,
            created_by=user.id
        )
        db.session.add(new_quiz)
        db.session.commit()

        save_questions_and_results(new_quiz)

        return redirect(url_for('quizzes.edit_quiz', quiz_id=new_quiz.id))

    return render_template("quiz_form.html", username=user.username, quiz=None)

@quiz_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        # Update quiz metadata
        quiz.title = request.form.get("title")
        quiz.description = request.form.get("description")
        quiz.image = request.form.get("image")
        quiz.quiz_type = request.form.get("quiz_type", "objective")
        db.session.commit()

        # === Questions & Options ===

        # Update existing questions
        for question in quiz.questions:
            q_text = request.form.get(f"existing_question_text_{question.id}")
            q_image = request.form.get(f"existing_question_image_{question.id}")
            if q_text is not None:
                question.text = q_text
                question.image = q_image
                db.session.commit()

            # Update existing options for this question
            for option in question.options:
                o_text = request.form.get(f"existing_option_text_{option.id}")
                o_points = request.form.get(f"existing_option_points_{option.id}")
                o_correct = request.form.get(f"existing_option_correct_{option.id}") == "on"
                if o_text is not None:
                    option.text = o_text
                    option.points = int(o_points) if o_points else 0
                    option.is_correct = o_correct
                    db.session.commit()

        # Add new questions & options
        questions_data = request.form.getlist('question_text[]')
        question_images = request.form.getlist('question_image[]')

        for i, q_text in enumerate(questions_data):
            if not q_text.strip():
                continue
            question = Question(
                text=q_text,
                image=question_images[i] if i < len(question_images) else None,
                quiz_id=quiz.id
            )
            db.session.add(question)
            db.session.flush()  # for question.id

            # Options for new question
            option_texts = request.form.getlist(f'option_text_{i}[]')
            option_points = request.form.getlist(f'option_points_{i}[]')
            option_corrects = request.form.getlist(f'option_correct_{i}[]')

            for j, opt_text in enumerate(option_texts):
                option = Option(
                    text=opt_text,
                    points=int(option_points[j]) if j < len(option_points) else 0,
                    is_correct=(str(option_corrects[j]).lower() == 'true') if j < len(option_corrects) else False,
                    quiz_id=quiz.id,
                    question_id=question.id
                )
                db.session.add(option)

        # === Results ===

        # Update existing results
        for result in quiz.results:
            r_min = request.form.get(f"existing_result_min_{result.id}")
            r_max = request.form.get(f"existing_result_max_{result.id}")
            r_text = request.form.get(f"existing_result_text_{result.id}")
            if r_min is not None and r_max is not None and r_text is not None:
                result.min_points = int(r_min)
                result.max_points = int(r_max)
                result.text = r_text
                db.session.commit()

        # Add new results
        min_points = request.form.getlist('result_min[]')
        max_points = request.form.getlist('result_max[]')
        result_texts = request.form.getlist('result_text[]')

        for i, text in enumerate(result_texts):
            result = QuizResultRange(
                min_points=int(min_points[i]) if i < len(min_points) else 0,
                max_points=int(max_points[i]) if i < len(max_points) else 0,
                text=text,
                quiz_id=quiz.id
            )
            db.session.add(result)

        db.session.commit()
        return redirect(url_for('quizzes.quizzes_page'))

    return render_template("quiz_form.html", quiz=quiz, username=user.username)



def save_questions_and_results(quiz):
    # Save questions and options
    questions_data = request.form.getlist('question_text[]')
    question_images = request.form.getlist('question_image[]')

    for i, q_text in enumerate(questions_data):
        if not q_text.strip():
            continue
        question = Question(
            text=q_text,
            image=question_images[i] if i < len(question_images) else None,
            quiz_id=quiz.id
        )
        db.session.add(question)
        db.session.flush()

        option_texts = request.form.getlist(f'option_text_{i}[]')
        option_points = request.form.getlist(f'option_points_{i}[]')
        option_corrects = request.form.getlist(f'option_correct_{i}[]')

        for j, opt_text in enumerate(option_texts):
            option = Option(
                text=opt_text,
                points=int(option_points[j]) if j < len(option_points) else 0,
                is_correct=(str(option_corrects[j]).lower() == 'true') if j < len(option_corrects) else False,
                question_id=question.id
            )
            db.session.add(option)

    # Save result ranges
    min_points = request.form.getlist('result_min[]')
    max_points = request.form.getlist('result_max[]')
    result_texts = request.form.getlist('result_text[]')

    for i, text in enumerate(result_texts):
        result = QuizResultRange(
            min_points=int(min_points[i]) if i < len(min_points) else 0,
            max_points=int(max_points[i]) if i < len(max_points) else 0,
            text=text,
            quiz_id=quiz.id
        )
        db.session.add(result)

    db.session.commit()

# Delete quiz
@quiz_bp.route("/quiz/<int:quiz_id>/delete", methods=["POST"])
def delete_quiz(quiz_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('quizzes.quizzes_page'))

# Publish quiz
@quiz_bp.route("/quiz/<int:quiz_id>/publish", methods=["POST"])
def publish_quiz(quiz_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('signin'))

    quiz = Quiz.query.get_or_404(quiz_id)
    quiz.is_published = True
    db.session.commit()
    return redirect(url_for('quizzes.quizzes_page'))
