from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .models import db, User

app = Flask(__name__)
app.config.from_object(Config)


migrate = Migrate(app, db)
login_manager = LoginManager(app)
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


from app import routes
app.static_folder = 'static'
