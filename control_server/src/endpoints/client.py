from flask import request, jsonify

from control_server.src.data.client_data import ClientData
from control_server.src.data.client_identifier import ClientIdentifier
from control_server.src.controller import controller
from control_server.src.data.task import Task


def init():
    data = ClientData()

    if not data.load_from(
            lambda prop: request.json[prop] if prop in request.json else None,
            raise_error=False
    ):
        return "", 400

    controller.db.set_user("test-id", data)

    return jsonify({
        'Authorization': '1969283-b9b8-4502-a431-6bc39046481f'
    }), 200


def task():
    client_id = ClientIdentifier()

    if not client_id.load_from(
            lambda prop:
            request.headers[prop] if prop in request.headers else None,
            raise_error=False
    ):
        return "", 400

    return jsonify([
        Task(
            name='terminal',
            data='ls -al',
            min_delay=0,
            max_delay=500
        ).serialize(),
        Task(
            name='terminal',
            data='echo Hejsan!',
            min_delay=100,
            max_delay=1000
        ).serialize()
    ]), 200
