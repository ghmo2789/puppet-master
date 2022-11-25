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


def client_tasks():
    """
    Endpoint handling when a task is given to the a client or all the tasks
    a client has been given previously.
    :return: A list of task or status code when a task is saved successfully
    in the database depending on the request.
    """
    # Task class representing a client task
    # ClientTask class representing a task assigned to a client
    auth = request.headers.get('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    # POST är för att en admin ska kunna ge en client en task
    if request.method == 'POST':

        incoming = request.get_json()
        clients_id = incoming.get('client_id')
        task_to_send = incoming.get('data')
        min_delay = incoming.get('min_delay')
        max_delay = incoming.get('max_delay')

        if clients_id is None or task_to_send is None:
            return 'Missing ID or task', 400

        # Check if client exist
        # Client is a IdentifyingClientData
        for current_client in clients_id.split(', '):
            client_exist = controller.db.get_user(current_client)

            if client_exist is None:
                return 'Client does not exists', 404

            new_task = Task(
                task_to_send,   # Task name
                task_to_send,   # The task itself
                int(min_delay),
                int(max_delay)
            )
            new_task.generate_id()

            client_task = ClientTask(
                client_exist.id,
                new_task.task_id,
                new_task
            )
            controller.db.set(
                collection=DatabaseCollection.USER_TASKS,
                entry_id=client_task.task_id,
                entry=client_task,
                overwrite=True
            )
        return '', 200

    # method == GET
    # GET är för att adminen ska kunna hämta tasks som en client har kört
    else:

        client_id = request.args.get('id')
        task_to_get = request.form.get('task')

        # Wrong client id or bad formatting
        if client_id is None or len(client_id) == 0:
            return 'Missing client id', 400

            # Check if task exist
            # Current task is a Task()
        current_task = controller.db.get_one(
            collection=DatabaseCollection.USER_TASKS,
            entry_id=task_to_get,
            entry_instance=Task()
        )
        if current_task is None:
            return 'Task does not exists', 404

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

