from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Challenge, User, Flag, db, Submission
from flask import Blueprint
from datetime import datetime, date


admin = Blueprint('admin', __name__)

# Helper function for admin-only access
def admin_only():
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.dashboard'))
    
# Admin Dashboard
@admin.route('/admin_dashboard')
@login_required
def admin_dashboard():
    admin_only()
    
    # Quick Stats Data
    total_challenges = Challenge.query.count()
    public_challenges = Challenge.query.filter_by(visibility='public').count()
    private_challenges = Challenge.query.filter_by(visibility='private').count()
    
    active_users = User.query.count()
    public_users = User.query.filter_by(profile_visibility='public').count()
    private_users = User.query.filter_by(profile_visibility='private').count()
    
    solves_today = Submission.query.filter_by(correct=True).filter(
        db.func.date(Submission.timestamp) == date.today()
    ).count()
    solves_today_public_users = Submission.query.filter_by(correct=True).join(User).filter(
        User.profile_visibility == 'public',
        db.func.date(Submission.timestamp) == date.today()
    ).count()
    solves_today_private_users = Submission.query.filter_by(correct=True).join(User).filter(
        User.profile_visibility == 'private',
        db.func.date(Submission.timestamp) == date.today()
    ).count()
    
    return render_template('admin_dashboard.html', 
                           total_challenges=total_challenges,
                           public_challenges=public_challenges,
                           private_challenges=private_challenges,
                           active_users=active_users,
                           public_users=public_users,
                           private_users=private_users,
                           solves_today=solves_today,
                           solves_today_public_users=solves_today_public_users,
                           solves_today_private_users=solves_today_private_users)

# Challenge Management Pages
@admin.route('/admin/challenges/add')
@login_required
def add_challenge_page():
    admin_only()
    return render_template('admin_add_challenge.html')

# admin remove challenge page
@admin.route('/admin/challenges/remove')
@login_required
def remove_challenge_page():
    admin_only()
    challenges = Challenge.query.all()
    return render_template('admin_remove_challenge.html', challenges=challenges)

# admin edit challenge page
@admin.route('/admin/challenges/edit')
@login_required
def edit_challenge_page():
    admin_only()    
    challenges = Challenge.query.all()
    return render_template('admin_edit_challenge.html', challenges=challenges)

# User Management Pages
@admin.route('/admin/users/add')
@login_required
def add_user_page():
    admin_only()
    return render_template('admin_add_user.html')

# admin remove user page
@admin.route('/admin/users/remove')
@login_required
def remove_user_page():
    admin_only()
    users = User.query.all()
    return render_template('admin_remove_user.html', users=users)

# admin edit user page
@admin.route('/admin/users/edit')
@login_required
def edit_user_page():
    admin_only()
    users = User.query.all()
    return render_template('admin_edit_user.html', users=users)

# Visibility Management Page
@admin.route('/admin/visibility')
@login_required
def visibility_page():
    admin_only()
    users = User.query.all()
    challenges = Challenge.query.all()
    return render_template('admin_visibility.html', users=users, challenges=challenges)

# add challenges
@admin.route('/admin/challenges/add', methods=['POST'])
@login_required
def add_challenge():

    admin_only()

    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')
    difficulty = request.form.get('difficulty')
    score = int(request.form.get('score'))
    flags = request.form.get('flags')  # Get flags as string
    flags_list = flags.split(',') if flags else []  # Convert to list

    print(description)
    new_challenge = Challenge(title=title, description=description, category=category, difficulty=difficulty, score=score)
    db.session.add(new_challenge)
    db.session.commit()

    for flag in flags_list:
        new_flag = Flag(challenge_id=new_challenge.id, flag=flag.strip())
        db.session.add(new_flag)

    db.session.commit()
    flash("Challenge added successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

# edit challenges
@admin.route('/admin/challenges/edit/<int:challenge_id>', methods=['POST'])
@login_required
def edit_challenge(challenge_id):

    admin_only()

    challenge = Challenge.query.get_or_404(challenge_id)
    challenge.title = request.form.get('title')
    challenge.description = request.form.get('description')
    challenge.category = request.form.get('category')
    challenge.difficulty = request.form.get('difficulty')
    challenge.score = int(request.form.get('score'))
    challenge.file_link = request.form.get('file_link')

    # Update flags
    flags = request.form.get('flags')
    flags_list = flags.split(',') if flags else []

    # Delete existing flags
    Flag.query.filter_by(challenge_id=challenge_id).delete()

    # Add new flags
    for flag in flags_list:
        new_flag = Flag(challenge_id=challenge.id, flag=flag.strip())
        db.session.add(new_flag)

    db.session.commit()
    flash("Challenge updated successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

# remove challenges
@admin.route('/admin/challenges/delete/<int:challenge_id>', methods=['POST'])
@login_required
def remove_challenge(challenge_id):

    admin_only()
    
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    flash('Challenge deleted successfully', 'danger')
    return redirect(url_for('admin.admin_dashboard'))

# admin users
@admin.route('/admin/users', methods=['POST'])
@login_required
def add_new_users():
    admin_only()

    username = request.form.get('username')
    password = request.form.get('password')  # Hash the password before saving

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("Username already exists!", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    flash("User added successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))


# admin remove users
@admin.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def remove_user(user_id):
    admin_only()

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'danger')
    return redirect(url_for('admin.admin_dashboard'))


# admin edit users
@admin.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):

    admin_only()

    user = User.query.get_or_404(user_id)
    user.username = request.form.get('username')
    user.set_password(request.form.get('password'))
    db.session.commit()
    flash('User updated successfully', 'info')
    return redirect(url_for('admin.admin_dashboard'))


# Update User Visibility
@admin.route('/admin/users/visibility/<int:user_id>', methods=['POST'])
@login_required
def update_user_visibility(user_id):
    admin_only()
    user = User.query.get_or_404(user_id)
    new_visibility = request.form.get('visibility')
    if new_visibility in ['public', 'private']:
        user.profile_visibility = new_visibility
        db.session.commit()
        flash(f"User {user.username}'s visibility updated to {new_visibility}", "success")
    else:
        flash("Invalid visibility value", "danger")
    return redirect(url_for('admin.visibility_page'))

# Update Challenge Visibility
@admin.route('/admin/challenges/visibility/<int:challenge_id>', methods=['POST'])
@login_required
def update_challenge_visibility(challenge_id):
    admin_only()
    challenge = Challenge.query.get_or_404(challenge_id)
    new_visibility = request.form.get('visibility')
    if new_visibility in ['public', 'private']:
        challenge.visibility = new_visibility
        db.session.commit()
        flash(f"Challenge {challenge.title}'s visibility updated to {new_visibility}", "success")
    else:
        flash("Invalid visibility value", "danger")
    return redirect(url_for('admin.visibility_page'))
