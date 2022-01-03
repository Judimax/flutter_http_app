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
from flask_marshmallow import Marshmallow
import pprint
import json
import my_util
import requests
import time

app = Flask(__name__)
app.config.update(
    # SERVER_NAME="127.0.0.1:5000",
    USE_NGROK=False,
    FLASK_ENV = 'production',
    SECRET_KEY=os.environ.get("FLASK_SOCKET_IO_SECRET_KEY")
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
ma = Marshmallow(app)
import users
import cart
import products
import orders
import my_init
#

db.create_all()
my_init.init_products()
my_init.init_orders()
my_init.init_users()

# socketIo
sio = SocketIO(app,cors_allowed_origins="https://michaelodumosu57.github.io")
@sio.event
def connect():
    print("connected")

@sio.on('my event')
def test_message(message):
    sio.emit('my response', {'data': message['data']})

@sio.on('my broadcast event')
def test_message(message):
    sio.emit('my response', {'data': message['data']}, broadcast=True)


@sio.on('connect')
def test_connect():
    sio.emit('my response', {'data': 'Connected'})

@sio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
# 

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
  return response


@app.route('/i18n_translate_vendor',methods=['POST'])
def i18n_translate_vendor():
    data  = request.json['data']
    my_util.i18n_translate_vendor(data)
    return {
        'msg':'OK'
    },200

if __name__ == "__main__":
    port = 5000
    if app.config['USE_NGROK']:
        public_url = ngrok.connect(port).public_url
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))
        app.config["BASE_URL"] = public_url
    app.run(debug=True)

