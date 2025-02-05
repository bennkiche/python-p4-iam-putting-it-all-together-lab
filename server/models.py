from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

from config import db, bcrypt


Base = declarative_base()

class User(db.Model):
    __tablename__ = 'users'
    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String(128), nullable=False)
    image_url = db.Column(db.String ,default='')
    bio = db.Column(db.String ,default='')

    # Ensure the relationship to Recipe is correctly set up
    recipes = db.relationship('Recipe', backref='user', lazy=True)
    

    # Prevent reading password directly
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    def authenticate(self, password):
        return self.check_password(password)
        
class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @staticmethod
    def validate_instructions_length(target, value, oldvalue, initiator):
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value


# Apply validation for instructions length
event.listen(Recipe.instructions, 'set', Recipe.validate_instructions_length, retval=True)
