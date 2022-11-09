from typing import Dict, Any

from flask import request, jsonify

from control_server.src.data.client_data import ClientData
from control_server.src.data.client_identifier import ClientIdentifier
from control_server.src.data_class import DataClass
from control_server.src.controller import get_controller

controller = get_controller()
app = controller.app
prefix = controller.url_prefix


def get_app():
    return app


@app.route(f"{prefix}/client/init", methods=["POST"])
def init():
    data = ClientData()

    if not data.load_from(lambda prop:
                          request.json[prop] if prop in request.json else None):
        return "", 400

    controller.db.set_user("test-id", data)
    return "", 200


@app.route(f"{prefix}/client/task", methods=["GET"])
def task():
    client_id = ClientIdentifier()

    if not client_id.load_from(
            lambda prop:
            request.headers[prop] if prop in request.headers else None):
        return "", 400

    return jsonify([]), 200
