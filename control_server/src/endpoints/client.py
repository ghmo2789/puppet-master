from flask import request, jsonify

from control_server.src.data.client_data import ClientData
from control_server.src.data.client_identifier import ClientIdentifier
from control_server.src.controller import controller
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.task import Task
from control_server.src.utils.request_utils import get_ip


def init():
    """
    Endpoint handling the client init request
    :return: A generated client id and a status code representing whether
    the request was successful or not, and why it may have been unsuccessful
    """
    data = ClientData.load_from_dict(request.json, raise_error=False)

    # Try to load client data from the body of the received POST request
    if data is None:
        return "", 400  # If unsuccessful, return 400 Bad Request

    # Generate a client id from the client data
    client_ip = get_ip(request)
    identifying_client_data = IdentifyingClientData(
        client_data=data,
        ip=client_ip
    )

    client_id = controller.client_id_generator.generate(identifying_client_data)

    if client_id is None:
        print(f"Failed to generate client id for client with IP "
              f"{request.remote_addr}.")
        return "", 500  # If unsuccessful, return 500 Internal Server Error

    client_id = str(client_id)

    controller.db.set_user(
        user_id=client_id,
        user=identifying_client_data,
        overwrite=True)

    return jsonify({
        'Authorization': client_id
    }), 200


def task():
    """
    Endpoint handing the client task request
    :return: A list of tasks, if any, and a status code representing whether
    the request was successful or not, and why it may have been unsuccessful
    """
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
