from typing import cast, List

from flask import request, jsonify
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.identifying_client_data import IdentifyingClientData
from control_server.src.data.client_data import ClientData
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable


def client():
    # TODO: Add authorization check
    """
    Endpoint handing the client information request from admin GUI
    :return: Clients information and a status code for representing the request was successful
     or not and why it may have been unsuccessful, if clients id is missing or
    """
    client_id = request.args.get('id')
    print(client_id)
    if client_id is None or len(client_id) == 0:
        return 'Missing client id', 400

    client_info = controller.db.get_user(
        client_id,
    )
    if client_info is None:
        return 'Wrong client id', 404

    return client_info.serialize(), 200


def allclients():
    # TODO: Add authorization check
    """
    Endpoint handling all the clients information request from admin GUI
    :return:
    """
    identifier = {}
    for key, value in request.args.items():
        identifier[key] = value

    all_clients = cast(
        List[ClientData],
        list(controller.db.get_all(collection=DatabaseCollection.USERS,
                                   identifier=identifier,
                                   entry_instance_creator=lambda: cast(Deserializable,
                                                                       ClientData()))
             ))
    print(all_clients)
    return jsonify({
        'all_clients': all_clients
    }), 200
