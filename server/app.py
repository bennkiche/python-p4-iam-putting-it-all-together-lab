

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe
from flask import jsonify


class Signup(Resource):
    def post(self):
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return {'error': 'Username and password are required'}, 422  

        try:
            new_user = User(
                username=data['username'],
                image_url=data.get('image_url', ''),
                bio=data.get('bio', '')
            )
            new_user.password = data['password']  
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id  

            return {   
                'id': new_user.id,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }, 201

        except IntegrityError:  
            db.session.rollback()
            return {'error': 'Username already exists'}, 422

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500  



class Login(Resource):
    def post(self):
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return {'error': 'Username and password are required'}, 401  

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            session['user_id'] = user.id  
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200  

        return {'error': 'Invalid username or password'}, 401  


class Logout(Resource):
    def delete(self):
        # Check if the user is logged in
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401
        
        # Clear the session if user is logged in
        session.pop('user_id', None)
        return {}, 204




class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401 

        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 401  

        return {
            'id': user.id,
            'username': user.username,
            'image_url': user.image_url,
            'bio': user.bio
        }, 200  


class RecipeIndex(Resource):
    def get(self):
        # Validate user session
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        return [recipe.to_dict() for recipe in user.recipes], 200


        
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        request_json = request.get_json()

        title = request_json.get('title')
        instructions = request_json.get('instructions')
        minutes_to_complete = request_json.get('minutes_to_complete')

        if not all([title, instructions, minutes_to_complete]):
            return {'error': 'Missing required fields'}, 422

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id,
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'Unprocessable Entity'}, 422
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)