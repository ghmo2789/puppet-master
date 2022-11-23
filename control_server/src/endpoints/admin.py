from typing import cast, List

from flask import request, jsonify
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.client_task import ClientTask


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


def task():
    """
    Endpoint handling when a task is given to the a client or all the tasks
    a client has been given previously.
    :return: A list of task or status code when a task is saved successfully
    in the database depending on the request.
    """
    auth = request.headers.get('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    # POST är för att en admin ska kunna ge en client en task
    if request.method == 'POST':
        pass


    # method == GET
    # GET är för att adminen ska kunna hämta tasks som en client har kört
    else:

        client_id = request.args.get('id')

        # Wrong client id or bad formatting
        if client_id is None or len(client_id) == 0:
            return 'Missing client id', 400

        # Check if client exist in DB
        client_info = controller.db.get_user(
            client_id
        )
        if client_info is None:
            return 'Client does not exist', 404

        # Get all the tasks for given client
        all_tasks_db = cast(
            List[ClientTask],
            list(controller.db.get_all(
                collection=DatabaseCollection.USER_DONE_TASKS,
                identifier={
                    'client_id': client_id
                },
                entry_instance_creator=lambda: cast(
                    Deserializable,
                    ClientTask
                )
            ))
        )

        # No task exits for the given client
        if len(all_tasks_db) == 0:
            return 'No tasks are send to the client', 404

        return jsonify({
            'all_tasks': [current_task.serialize() for current_task in all_tasks_db]
        }), 200


def all_tasks():
    # TODO: All tasks or all tasks and all done tasks.
    auth = request.headers('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    all_tasks_db = cast(
        List[ClientTask],
        list(
            controller.db.get_all(
                collection=DatabaseCollection.USER_TASKS,
                identifier={},
                entry_instance_creator=lambda: cast(
                    Deserializable,
                    ClientTask
                )
            ))
    )

    if len(all_tasks_db) == 0:
        return 'No tasks exist', 404

    return jsonify({
        'all_tasks': [current_task.serialize() for current_task in all_tasks()]
    }), 200

