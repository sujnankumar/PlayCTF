from flask import render_template, Blueprint, flash, redirect, request, url_for

from flask_login import login_required, current_user
from models import User, Challenge, Flag, Submission, db

main = Blueprint("main", __name__)
# admin = Blueprint('admin', __name__)


# landing page
@main.route('/')
def home():
    return render_template('index.html')

# user dashboard
@main.route('/dashboard')
@login_required
def dashboard():
    challenges = Challenge.query.all()
    return render_template('dashboard.html', challenges=challenges)

# submitting flag
@main.route('/submit_flag', methods=['POST'])
@login_required
def submit_flag():
    challenge_id = request.form.get('challenge_id')
    submitted_flag = request.form.get('flag')

    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        flash("Challenge not found!", "danger")
        return redirect(url_for('main.dashboard'))
    print(submitted_flag)

    correct_flag = Flag.query.filter_by(challenge_id=challenge.id, flag=submitted_flag).first()
    print(correct_flag)
    if correct_flag:
        current_user.score += challenge.score
        db.session.commit()
        flash("Correct flag! Points awarded.", "success")
    else:
        flash("Incorrect flag! Try again.", "danger")

    return redirect(url_for('main.dashboard'))

# list users
@main.route('/users')
@login_required
def users():
    search_query = request.args.get('search', '')
    if search_query:
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
    else:
        users = User.query.all()
    return render_template('users.html', users=users, search_query=search_query)


# scoreboard
@main.route('/scoreboard')
def scoreboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template('scoreboard.html', users=users)

