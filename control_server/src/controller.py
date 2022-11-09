from flask import Flask

from control_server.src.db import Database
from control_server.src.web_settings import WebSettings


class Controller:
    def __init__(self):
        self._settings = WebSettings().read()
        self._app = Flask(__name__)
        self.app.debug = True
        self._db = Database()

    @property
    def app(self):
        return self._app

    @property
    def settings(self):
        return self._settings

    @property
    def url_prefix(self):
        return self.settings.prefix

    @property
    def db(self):
        return self._db


controller = Controller()


def get_controller():
    return controller
