from flask import Flask
from config import Config
from routes import main
from admin_routes import admin
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User
from auth import auth

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

# Initialize Flask-Migrate (This is important)
migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints (Routes)
app.register_blueprint(main)
app.register_blueprint(admin)
app.register_blueprint(auth, url_prefix='/auth')


if __name__ == "__main__":
    app.run(debug=True)
