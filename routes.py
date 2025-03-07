from flask import render_template, Blueprint, flash, redirect, request, url_for, jsonify    

from flask_login import login_required, current_user
from models import User, Challenge, Flag, Submission, db


main = Blueprint("main", __name__)
# admin = Blueprint('admin', __name__)


# landing page
@main.route('/')
def home():
    return render_template('index.html')

# challenges 
@main.route('/challenges')
@login_required
def dashboard():
    if current_user.is_admin:
        # Get all challenges for admin
        challenges = Challenge.query.all()
    else:
        # Get only public challenges for non-admin users
        challenges = Challenge.query.filter_by(visibility="public").all()

    # Get IDs of challenges the user has correctly solved
    solved_challenge_ids = {int(sub.challenge_id) for sub in Submission.query.filter_by(user_id=current_user.id, correct=True).all()}

    return render_template('dashboard.html', challenges=challenges, solved_challenges=solved_challenge_ids)


# submitting the flag
@main.route('/submit_flag', methods=['POST'])
@login_required
def submit_flag():
    challenge_id = request.form.get('challenge_id')
    submitted_flag = request.form.get('flag')

    if submitted_flag.strip() == '':
        return jsonify({"message": "Enter flag first!", "category": "warning"}), 400

    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({"message": "Challenge not found!", "category": "danger"}), 400

    # Check if the user has already solved this challenge
    previous_submission = Submission.query.filter_by(
        user_id=current_user.id, 
        challenge_id=challenge.id, 
        correct=True
    ).first()
    
    if previous_submission:
        return jsonify({"message": "Already solved this challenge!", "category": "warning"}), 400

    # Check if the flag is correct
    correct_flag = Flag.query.filter_by(challenge_id=challenge.id, flag=submitted_flag).first()
    is_correct = correct_flag is not None

    # Store the submission
    new_submission = Submission(
        user_id=current_user.id,
        challenge_id=challenge.id,
        submitted_flag=submitted_flag,
        correct=is_correct
    )
    db.session.add(new_submission)

    # Award points only if correct and first time solving
    if is_correct:
        current_user.score += challenge.score
        db.session.commit()
        return jsonify({"message": "Correct flag! Points awarded.", "category": "success", "correct": True}), 200
    else:
        db.session.commit()
        return jsonify({"message": "Incorrect flag! Try again.", "category": "danger", "correct": False}), 400


# list users
@main.route('/users')
@login_required
def users():
    search_query = request.args.get('search', '')
    if search_query:
        if current_user.is_admin:
            users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
        else:
            users = User.query.filter(User.username.ilike(f"%{search_query}%"), User.profile_visibility == "public").all()
    else:
        if current_user.is_admin:
            users = User.query.all()
        else:
            users = User.query.filter_by(profile_visibility="public").all()
    return render_template('users.html', users=users, search_query=search_query)


# scoreboard
@main.route('/scoreboard')
def scoreboard():
    scored_users = User.query.filter(User.score > 0, User.profile_visibility == "public").order_by(User.score.desc()).all()

    return render_template('scoreboard.html', users=scored_users)

