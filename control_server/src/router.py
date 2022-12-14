from __future__ import annotations

import sys
from typing import List, Callable, Dict

from decouple import config, Choices
from flask import Flask

from control_server.src.controller import Controller
from control_server.src.endpoints import client
from control_server.src.endpoints import admin
from control_server.src.middleware.forwarding_udp_control_listener import \
    ForwardingUdpControlListener


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

    def __init__(self, enable_http: bool = False):
        self._controller = Controller(
            lightweight_mode=not enable_http
        )

        if enable_http:
            self._app = Flask(__name__)
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
            ),
            RouteDestination(
                f'{pref}/admin/taskoutput',
                admin.get_task_output,
                ['GET']
            )
        ]

        self.endpoints: Dict[str, List[RouteDestination]] = {}

        for route in self.route_map:
            if enable_http:
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


router: Router
app: Flask | None
_is_flask: bool = True


def init():
    global router, app
    is_testing = "pytest" in sys.modules
    mode = config(
        'MODE',
        default='both',
        cast=Choices(['http', 'udp', 'both'])
    )

    is_both = mode == 'both'

    if mode == 'http' or is_both:
        router = Router(
            enable_http=True
        )
        app = router.app

    if mode == 'udp' or is_both:
        if not is_both:
            router = Router(
                enable_http=is_both
            )
            app = None

        if not is_testing:
            listener = ForwardingUdpControlListener(
                port=config(
                    'UDP_PORT',
                    default=36652,
                    cast=int
                ),
                host=config(
                    'UDP_HOST',
                    default='0.0.0.0',
                    cast=str
                ),
                route_validator=lambda route: router.has_route(route),
                api_base_url=config('FORWARD_TO_HOST'),
                ignore_route_check=False
            )

            listener.start()
            print(f' * UDP listener started on '
                  f'{listener.udp_server.host}:{listener.udp_server.port}')

    if mode == 'http' or is_both:
        return app

    return None


if __name__ == '__main__':
    _is_flask = False
    init()
