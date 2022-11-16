from flask import Request
from control_server.src.controller import controller


def get_ip(request: Request) -> str:
    """
    Gets the IP address of the client from the request
    :param request: The request to get the IP address from
    :return: The IP address of the client
    """
    return \
        request.access_route[-1] if controller.settings.behind_proxy else \
        request.remote_addr
