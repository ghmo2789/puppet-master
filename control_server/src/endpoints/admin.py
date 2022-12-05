from typing import cast, List

from flask import request, jsonify
from control_server.src.controller import controller
from control_server.src.data.task_status import TaskStatus
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
        'all_clients': [current_client.serialize() for current_client in
                        all_clients_db]
    }), 200


def get_client_tasks():
    """
    Endpoint handling when a task is given to the a client or all the tasks
    a client has been given previously.
    :return: if post status code for successfully operation otherwise another
    status code with an error message. If GET a list of tasks that were send
    to the given client and a list of tasks that were executed successfully
    on the given client.
    """
    # Task class representing a client task
    # ClientTask class representing a task assigned to a client
    auth = request.headers.get('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    client_id = request.args.get('id')
    task_id = request.args.get('task_id')

    key = {

    }

    # Wrong client id or bad formatting
    if client_id is not None and len(client_id) > 0:
        # Check if client exist in DB
        client_info = controller.db.get_user(
            client_id
        )

        if client_info is None:
            return 'Client does not exist', 404

        key['_id.client_id'] = client_id

    # Wrong client id or bad formatting
    if task_id is not None and len(task_id) > 0:
        key['_id.task_id'] = task_id

    # Get all the tasks for given client
    all_tasks_db = cast(
        List[ClientTask],
        list(controller.db.get_all(
            collection=DatabaseCollection.USER_TASKS,
            identifier=key,
            entry_instance_creator=lambda: cast(
                Deserializable,
                ClientTask()
            )
        ))
    )

    # All the done tasks
    all_done_tasks = cast(
        List[ClientTask],
        list(controller.db.get_all(
            collection=DatabaseCollection.USER_DONE_TASKS,
            identifier=key,
            entry_instance_creator=lambda: cast(
                Deserializable,
                ClientTask()
            )
        ))
    )

    return jsonify({
        'pending_tasks': [current_task.serialize() for current_task in
                          all_tasks_db],
        'sent_tasks': [
            [current_task.serialize() for current_task in all_done_tasks]]
    }), 200


def post_client_tasks():
    """
    Endpoint handling when a task is given to the a client or all the tasks
    a client has been given previously.
    :return: if post status code for successfully operation otherwise another
    status code with an error message. If GET a list of tasks that were send
    to the given client and a list of tasks that were executed successfully
    on the given client.
    """
    # Task class representing a client task
    # ClientTask class representing a task assigned to a client
    auth = request.headers.get('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    # POST är för att en admin ska kunna ge en client en task
    incoming = request.get_json()

    clients_id = incoming.get('client_id')
    task_data = incoming.get('data')
    task_name = incoming.get('name')
    min_delay = incoming.get('min_delay')
    max_delay = incoming.get('max_delay')

    if clients_id is None or task_data is None:
        return 'Missing ID or task', 400

    new_task = Task(
        name=task_name,
        data=task_data,
        min_delay=int(min_delay),
        max_delay=int(max_delay)
    )

    new_task.generate_id()

    clients = []

    # Check if client exist
    for current_client in clients_id.split(','):
        client_exist = controller.db.get_user(current_client.strip())

        if client_exist is None:
            return 'Client does not exist', 404

        clients.append(client_exist)

    for client_exist in clients:
        # Generate a task id
        new_client_task = ClientTask(
            client_id=client_exist.id,
            task_id=new_task.id,
            task=new_task
        )

        new_client_task.set_status(TaskStatus.PENDING)

        controller.db.set(
            collection=DatabaseCollection.USER_TASKS,
            entry_id=new_client_task.id,
            entry=new_client_task,
            overwrite=True
        )

    return new_task.id, 200
