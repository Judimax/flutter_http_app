import sys

if sys.platform == "win32":
    sys.path.append(sys.path[0] + "\\site-packages\\windows")
elif sys.platform =="linux":
    sys.path.append(sys.path[0] + "/site-packages/linux")
import pprint
import asyncio
from urllib.parse import urlparse, unquote
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
import threading
import logging
import json
import tornado.web
import tornado.ioloop
import template
from template import my_endpoint_client
import time
import datetime
import os
import multiprocessing
import importlib
from importlib import reload,util
pp = pprint.PrettyPrinter(indent=4, compact=True, width=1)




#  find the tables module for hot reload
class ModuleFinder(importlib.machinery.PathFinder):
    def __init__(self):
        self.path_map = {"template":template.__spec__.loader}

    def find_spec(self, fullname, path, target=None):

        if not fullname in self.path_map:
            return None
        return importlib.util.spec_from_loader(fullname, self.path_map[fullname])


    def find_module(self, fullname, path):
        return None # No need to implement, backward compatibility only
sys.meta_path.append(ModuleFinder())
#

# route handler
def createHandler(client):
    class MainHandler(tornado.web.RequestHandler):

        def set_default_headers(self):
            self.set_header("Access-Control-Allow-Origin", os.environ.get("FRONTEND_ORIGIN"))
            self.set_header("Access-Control-Allow-Headers", "*")
            self.set_header("Access-Control-Allow-Credentials","true")
            self.set_header("Allow-Origin-With-Credentials","true")
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')



        def post(self):
            data = ""
            if self.request.headers['Content-Type'] == 'application/json':
                data = tornado.escape.json_decode(self.request.body)
            elif self.request.headers['Content-Type'] == 'text/plain':
                data = json.loads(self.request.body)
            data["refresh_token"] = self.get_cookie('refresh_token')
            data["refresh_user"] = self.get_cookie('refresh_user')
            self.set_header("Content-Type", "text/plain")
            result = client.execute(client,data)

            try:
                refresh_token = result.get('refresh_token')
                if(refresh_token):
                    self.set_cookie("refresh_token",refresh_token,httponly=True)
                    self.set_cookie("refresh_user",result.get("refresh_user"),httponly=True)
                    # self.set_secure_cookie
                if(result.get("message") == 'Login Failed'):
                    result["message"] = json.dumps(
                        {"message":"There has been an issue please try again"}
                    )
                    self.set_header("WWW-Authenticate", 'Basic realm=:"Authentication Failed"')
            except:
                None
            self.set_status(result["status"])
            self.write(result["message"])
            self.finish()

        def options(self):
            self.set_status(204)
            self.finish()

    return MainHandler
#

# configuring web server
PORT = 3005
server = ""
ioloop = tornado.ioloop.IOLoop.current()
restart_server = False
my_client = my_endpoint_client()

def assign_me():
    pass

def start_app(*args, **kwargs):
    loading_error = True
    my_endpoint_client_code = None
    while loading_error:
        try:
            reload(template)
            my_endpoint_client_code = template.my_endpoint_client().execute.__code__
            # my_client.env = template.my_endpoint_client().env
            loading_error = False
        except Exception as e:
            print("fix the error in the code you have modifed\n")
            print(e)
            time.sleep(1)
    assign_me.__code__ = my_endpoint_client_code
    my_client.execute = assign_me
    application = tornado.web.Application([
        (r"/", createHandler(my_client)),
    ])
    print("server listening on {}".format(PORT))
    server = application.listen(PORT)
    global restart_server
    restart_server = False
    return server


def restart_tornado():
    global restart_server
    global server
    # print("checking for file change")
    # print(restart_server)
    if(restart_server):
        print("updating the ibm_language client")
        server.stop()
        server = None
        server = start_app()
    ioloop.add_callback(ioloop.stop)




class WatchDogEvent(LoggingEventHandler):
    def on_modified(self, event):
        global restart_server
        restart_server = True




if __name__ == "__main__":


    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    observer = Observer()
    observer.schedule(WatchDogEvent(), path, recursive=True)
    server = start_app()
    observer.start()
    try:
        while True:
            ioloop.call_later(
                callback = restart_tornado,
                delay = 1
            )
            ioloop.start()
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()







