from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base

from config import db, bcrypt


Base = declarative_base()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Ensure the relationship to Recipe is correctly set up
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # Prevent reading password directly
    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    # Setter for password (sets the hashed password)
    @password.setter
    def password(self, plaintext_password):
        self._password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

    # Method to check password
    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
        
class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def validate_instructions_length(target, value, oldvalue, initiator):
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value


# Apply validation for instructions length
event.listen(Recipe.instructions, 'set', Recipe.validate_instructions_length, retval=True)
