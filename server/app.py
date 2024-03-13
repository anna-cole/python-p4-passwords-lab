#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class Signup(Resource):
    def post(self): # You will create a new user by capturing his entered username and password
        username = request.get_json()['username']
        password = request.get_json()['password']
        if username and password:
            new_user = User(username=username)
            new_user.password_hash = password # hash his password 
            db.session.add(new_user) # add this new user in the db and save
            db.session.commit()
            session['user_id'] = new_user.id #save the user's ID in the session object
            return new_user.to_dict(), 201 #return the user obj in the JSON response
        return {'error': '422 Unprocessable Entity'}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id'] # you need to retrieve the user id from the session object
        if user_id: # if you find the user id that means it was assigned to a session and that means the user is already logged in. Then you return the user obj converted to json. If not, return empty json.
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        return {}, 204

class Login(Resource):
    def post(self):
        username = request.get_json().get('username') # This will get the username entered by the user. request.get_json() returns a dictionary, then you retrieve the username value.
        password = request.get_json().get('password') # retrieve the entered password
        user = User.query.filter(User.username == username).first() # With the username value you retrieve the user object.
        if user.authenticate(password): # if the password is authenticated then it will assign the user id to the session object
            session['user_id'] = user.id
            return user.to_dict(), 200 # return the user obj as JSON
        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        session['user_id'] = None # reassign the session obj to None, to delete the user id
        return {}, 204

api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
