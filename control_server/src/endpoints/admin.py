from typing import cast, List, Set
from datetime import datetime

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
    :return: Clients information and a status code for representing the
    request was successful
     or not and why it may have been unsuccessful, if clients id is missing or
    """

    auth = request.headers.get('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    client_id = request.args.get('id')
    if client_id is None or len(client_id) == 0:
        return 'Missing client id', 400

    client_info = controller.db.get_client(
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
        list(
            controller.db.get_all(
                collection=DatabaseCollection.CLIENTS,
                identifier={},
                entry_instance_creator=lambda: cast(
                    Deserializable,
                    IdentifyingClientData()
                )
            )
        )
    )

    # No client exists
    if len(all_clients_db) == 0:
        return '', 404

    return jsonify(
        {
            'all_clients': [current_client.serialize() for current_client in
                all_clients_db]
        }
    ), 200


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
        client_info = controller.db.get_client(
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
        list(
            controller.db.get_all(
                collection=DatabaseCollection.CLIENT_TASKS,
                identifier=key,
                entry_instance_creator=lambda: cast(
                    Deserializable,
                    ClientTask()
                )
            )
        )
    )

    # All the done tasks
    all_done_tasks = cast(
        List[ClientTask],
        list(
            controller.db.get_all(
                collection=DatabaseCollection.CLIENT_DONE_TASKS,
                identifier=key,
                entry_instance_creator=lambda: cast(
                    Deserializable,
                    ClientTask()
                )
            )
        )
    )

    return jsonify(
        {
            'pending_tasks': [current_task.serialize() for current_task in
                all_tasks_db],
            'sent_tasks': [
                [current_task.serialize() for current_task in all_done_tasks]]
        }
    ), 200


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

    # Current date and time
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M')

    if clients_id is None or task_data is None:
        return 'Missing ID or task', 400

    new_task = Task(
        name=task_name,
        data=task_data,
        min_delay=int(min_delay),
        max_delay=int(max_delay),
        date=date,
        time=time,
    )

    new_task.generate_id()

    clients = []

    # Check if client exist
    for current_client in clients_id.split(','):
        client_exist = controller.db.get_client(current_client.strip())

        if client_exist is None:
            return 'Client does not exist', 404

        clients.append(client_exist)

    ignore_clients: Set[str]
    if new_task.name == 'abort':
        ignore_clients = handle_abort_task(new_task)
    else:
        ignore_clients = set()

    # Add the abort task to the clients who are currently executing the task
    # that is being aborted
    for client_exist in clients:
        if client_exist.id in ignore_clients:
            continue

        # Generate a task id
        new_client_task = ClientTask(
            client_id=client_exist.id,
            task_id=new_task.id,
            task=new_task
        )

        new_client_task.set_status(TaskStatus.PENDING)

        controller.db.set(
            collection=DatabaseCollection.CLIENT_TASKS,
            entry_id=new_client_task.id,
            entry=new_client_task,
            overwrite=True
        )

    return new_task.id, 200


def handle_abort_task(
        abort_task: Task
) -> Set[str]:
    """
    Removes the task being aborted from all clients currently executing it.
    :param abort_task: The abort task, containing the task ids of the tasks
    being aborted.
    :return: A set of client IDs that the task being aborted was removed from.
    """
    result_clients = set()
    tasks_being_aborted = [
        task_id.strip() for task_id in abort_task.data.split(',')
    ]

    # Remove all referenced tasks from pending collection, add to done
    # collection instead. Flag the tasks as aborted.
    for task_id in tasks_being_aborted:
        tasks = controller.db.get_all(
            collection=DatabaseCollection.CLIENT_TASKS,
            identifier={
                '_id.task_id': task_id
            }
        )

        for aborted_task in tasks:
            result_clients.add(aborted_task.client_id)
            aborted_task.set_status(TaskStatus.ABORTED)
            controller.db.set(
                DatabaseCollection.CLIENT_DONE_TASKS,
                entry_id=aborted_task.id,
                entry=aborted_task,
                overwrite=True
            )

            controller.db.delete(
                DatabaseCollection.CLIENT_TASKS,
                entry_id=aborted_task.id
            )

            # Create an abort ClientTask for the client, and add it to the
            # clients done tasks, since the task being aborted was removed
            client_abort_task = ClientTask(
                client_id=aborted_task.client_id,
                task_id=abort_task.id,
                task=abort_task
            )

            client_abort_task.set_status(TaskStatus.DONE)

            controller.db.set(
                collection=DatabaseCollection.CLIENT_DONE_TASKS,
                entry_id=client_abort_task.id,
                entry=client_abort_task,
                overwrite=True
            )

    # Return set of clients who had a task aborted
    return result_clients
