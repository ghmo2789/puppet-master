from typing import List, Callable

from flask import Flask

from control_server.src.controller import Controller
from control_server.src.endpoints import client


class RouteDestination:
    """
    Data class used to store information about each route destination.
    Currently, a handler for a route and a list of allowed methods is stored.
    Class is used to set up routing in Router class.
    """
    def __init__(self, handler: Callable, methods: List[str]):
        self.name = handler.__name__
        self.handler = handler
        self.methods = methods


class Router:
    """
    Class used to set up the routing for the Flask app, and the Flask app
    itself.
    """

    def __init__(self):
        self._app = Flask(__name__)
        self._controller = Controller()
        self._app.debug = self._controller.settings.debug

        pref = self._controller.url_prefix
        self.route_map = {
            f'{pref}/client/init': RouteDestination(client.init, ['POST']),
            f'{pref}/client/task': RouteDestination(client.task, ['GET'])
        }

        for route, destination in self.route_map.items():
            self._app.add_url_rule(
                rule=route,
                endpoint=destination.name,
                view_func=destination.handler,
                methods=destination.methods)

    @property
    def app(self):
        return self._app


router = Router()
app = router.app