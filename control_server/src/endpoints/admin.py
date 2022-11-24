from typing import cast, List

from flask import request, jsonify
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.client_task import ClientTask
from control_server.src.data.task import Task


def client():
    """
    Endpoint handing the client information request from admin GUI
    :return: Clients information and a status code for representing the request was successful
     or not and why it may have been unsuccessful, if clients id is missing or
    """

    auth = request.headers.get('Authorization')
    print(auth)
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    client_id = request.args.get('id')
    if client_id is None or len(client_id) == 0:
        return 'Missing client id', 400

    client_info = controller.db.get_user(
        client_id,
    )
    if client_info is None:
        return 'Wrong client id', 404

    return client_info.serialize(), 200


def all_clients():
    """
    Endpoint handling all the clients information request from admin GUI
    :return: A list of all the clients in the database
    """

    auth = request.headers.get('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    all_clients_db = cast(
        List[IdentifyingClientData],
        list(controller.db.get_all(
            collection=DatabaseCollection.USERS,
            identifier={},
            entry_instance_creator=lambda: cast(
                Deserializable,
                IdentifyingClientData()
            )
        ))
    )

    # No client exists
    if len(all_clients_db) == 0:
        return '', 404

    return jsonify({
        'all_clients': [current_client.serialize() for current_client in all_clients_db]
    }), 200



