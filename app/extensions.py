from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()