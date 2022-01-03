import sys
if sys.platform == "win32":
    sys.path.append(sys.path[0] + "\\site-packages\\windows")
elif sys.platform =="linux":
    sys.path.append(sys.path[0] + "/site-packages/linux")
import json
import os
import uuid
import datetime
import time
import pprint
import asyncio
import json
import datetime
# import pytz
import time
pp = pprint.PrettyPrinter(indent=4, compact=True, width=1)
import random
import lorem
import jwt
import requests
from datetime import datetime,timedelta
from functools import wraps
import base64
import hashlib
import hmac
import pprint


# dev additons

# end

class my_endpoint_client():


    def error_handler(self,e,env):
        print('my custom error at {}\n'.format(env))
        print(e.__class__.__name__)
        print(e)
        return {
            'status':500,
            'message': 'an error occured check the output from the backend'
        }


    def __init__(self):
        self.datetime = datetime
        self.timedelta = timedelta
        self.time = time
        self.uuid = uuid
        self.random = random
        self.requests = requests
        self.lorem  = lorem
        self.jwt = jwt
        self.wraps = wraps

        # dev additions

        #


    def execute(self, data):

        #setup
        jwt = self.jwt
        timedelta = self.timedelta
        datetime = self.datetime
        time = self.time
        uuid = self.uuid
        random = self.random
        lorem = self.lorem
        requests = self.requests

        # dev additions

        #

        env = data.get("env")
        page = data.get('page')

        if(env == 'test_my_task'):
            print('-------------------')
            print('\n{}\n'.format('test_my_task'))
            try:
                my_task()
                return {
                    'status':200,
                    'message':{
                        'message':'OK'
                    }
                }

            except BaseException as e:
                return self.error_handler(e,env)


        return {
            "status" :500,
            "message": "Check the backend env dictionary you did set it so the backend didnt do anything"
        }











