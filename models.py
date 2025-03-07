from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)  # Track user score
    profile_visibility = db.Column(db.String(10), nullable=False, default="public")  # "public" or "private"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Difficulty level (Easy, Medium, Hard)
    score = db.Column(db.Integer, nullable=False)  # Points for solving the challenge
    visibility = db.Column(db.String(10), nullable=False, default="private")  # "public" or "private"
    
    flags = db.relationship('Flag', backref='challenge', lazy=True, cascade="all, delete")


class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    flag = db.Column(db.String(255), nullable=False)  # Store hashed flags for security
    # challenge = db.relationship('Challenge', backref=db.backref('flags', lazy=True))

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    submitted_flag = db.Column(db.String(255), nullable=False)
    correct = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('submissions', lazy=True))
    challenge = db.relationship('Challenge', backref=db.backref('submissions', lazy=True))
