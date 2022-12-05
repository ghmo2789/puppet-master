from __future__ import annotations
from typing import List, Callable, Tuple, Dict

from flask import Flask

from control_server.src.controller import Controller
from control_server.src.endpoints import client
from control_server.src.endpoints import admin


class RouteDestination:
    """
    Data class used to store information about each route destination.
    Currently, a handler for a route and a list of allowed methods is stored.
    Class is used to set up routing in Router class.
    """

    def __init__(self, route: str, handler: Callable, methods: List[str]):
        self.name = handler.__name__
        self.handler = handler
        self.methods = methods
        self.route = route


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
        self.route_map: List[RouteDestination] = [
            RouteDestination(
                f'{pref}/client/init',
                client.init,
                ['POST']
            ),
            RouteDestination(
                f'{pref}/client/task',
                client.task,
                ['GET']
            ),
            RouteDestination(
                f'{pref}/admin/client',
                admin.client,
                ['GET']
            ),
            RouteDestination(
                f'{pref}/admin/allclients',
                admin.all_clients,
                ['GET']
            ),
            RouteDestination(
                f'{pref}/client/task/response',
                client.task_response,
                ['POST']
            ),
            RouteDestination(
                f'{pref}/admin/task',
                admin.get_client_tasks,
                ['GET']
            ),
            RouteDestination(
                f'{pref}/admin/task',
                admin.post_client_tasks,
                ['POST']
            )
        ]

        self.endpoints: Dict[str, List[RouteDestination]] = {}

        for route in self.route_map:
            self._app.add_url_rule(
                rule=route.route,
                endpoint=route.name,
                view_func=route.handler,
                methods=route.methods)

            if route.route not in self.endpoints:
                self.endpoints[route.route] = []

            self.endpoints[route.route].append(route)

    def has_route(self, route: str):
        return route.lower() in self.endpoints

    @property
    def app(self):
        return self._app

    @property
    def controller(self):
        return self._controller


router: Router = Router()
app: Flask = router.app
