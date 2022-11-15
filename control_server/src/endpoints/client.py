from flask import request, jsonify

from control_server.src.data.client_data import ClientData
from control_server.src.data.client_identifier import ClientIdentifier
from control_server.src.controller import controller


def init():
    data = ClientData()

    if not data.load_from(
            lambda prop: request.json[prop] if prop in request.json else None,
            raise_error=False
    ):
        return "", 400

    controller.db.set_user("test-id", data)
    return "", 200


def task():
    client_id = ClientIdentifier()

    if not client_id.load_from(
            lambda prop:
            request.headers[prop] if prop in request.headers else None,
            raise_error=False
    ):
        return "", 400

    return jsonify([]), 200
