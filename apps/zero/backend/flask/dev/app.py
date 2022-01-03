import os
import sys
import my_util
my_util.local_deps()
from flask import Flask, request, redirect
from pyngrok import ngrok
from flask_socketio import SocketIO


# dev additions
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth
from flask_marshmallow import Marshmallow
import pprint
import json
import my_util
import requests
import time


app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_DATABASE_URI='sqlite:///crfdb.db',
    # SERVER_NAME="127.0.0.1:5000",
    USE_NGROK=False,
    FLASK_ENV = 'production',
    SECRET_KEY=os.environ.get("FLASK_SOCKET_IO_SECRET_KEY")
)
db = SQLAlchemy(app)
api = Api(app)
auth = HTTPBasicAuth()




class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    is_active = db.Column(db.Boolean)
    loyalty_points = db.Column(db.Integer)
    fitness_goal = db.Column(db.Integer)

class ExerciseProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.String)
    title = db.Column(db.String)
    reps = db.Column(db.Integer)


from seed_db import db_init
db_init()

@auth.verify_password
def verify_password(username, password):
    if len(ExerciseProfile.query.filter_by(username=username).filter_by(password=password).all()) > 0:
        return username

class ProgramResource(Resource):
    @auth.login_required
    def get(self):
        return [
            {
                'title': exercise.title,
                'reps': exercise.reps
            } for exercise in Exercise.query.filter_by(client=auth.current_user())
        ]

api.add_resource(ProgramResource, '/program')


class UserProfileResource(Resource):
    def get(self):
        return [
            {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'is_active': profile.is_active,
                'loyalty_points': profile.loyalty_points,
                'fitness_goal': profile.fitness_goal
            }
            for profile in UserProfile.query.all()
        ]

    def post(self):
        print(request.get_json())
        if len(UserProfile.query
            .filter_by(first_name=request.json['first_name'])
            .filter_by(last_name=request.json['last_name']).all()) > 0:
            return {'error': 'user exists'}, 409
        else:
            user = UserProfile(
                first_name=request.json['first_name'],
                last_name=request.json['last_name'],
                is_active=request.json['is_active'],
                loyalty_points=request.json['loyalty_points'],
                fitness_goal=request.json['fitness_goal']
            )
            db.session.add(user)
            db.session.commit()
            return {
                'id': user.id
            }, 201

api.add_resource(UserProfileResource, '/profile')



@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
  return response



if __name__ == "__main__":
    port = 5000
    if app.config['USE_NGROK']:
        public_url = ngrok.connect(port).public_url
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))
        app.config["BASE_URL"] = public_url
    app.run(debug=True)

