from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    recipes = db.relationship('Recipe', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def password(self):
        raise AttributeError("Password is not readable.")
    
    @password.setter
    def password(self, plaintext_password):
        self._password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    

class Recipe(db.Model, SerializerMixin):
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

# Apply validation
from sqlalchemy import event

event.listen(Recipe.instructions, 'set', Recipe.validate_instructions_length, retval=True)