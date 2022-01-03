import sys

if sys.platform == "win32":
    sys.path.append(sys.path[0] + "site-packages\\windows")
elif sys.platform =="linux":
    sys.path.append(sys.path[0] + "site-packages/linux")

from flask import Flask, request, redirect
from pyngrok import ngrok
import os
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
    # SERVER_NAME="127.0.0.1:3005",
    USE_NGROK=True
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



@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', os.environ.get("FRONTEND_ORIGIN"))
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
  return response



if __name__ == "__main__":
    port = 5000
    # public_url = ngrok.connect(port).public_url
    # print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))
    # app.config["BASE_URL"] = public_url
    app.run(debug=True)

