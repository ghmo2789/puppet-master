from typing import cast, List, Set, Iterable, Any, Optional, Callable
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
from control_server.src.data.client_task_response_collection import ClientTaskResponseCollection


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
        ignore_clients = _handle_abort_task(new_task)
    else:
        ignore_clients = set()

    # Add the abort task to the clients who are currently executing the task
    # that is being aborted
    for client_exist in clients:
        # If the task was an abort task, and the control server handled the
        # abort task for the current client, it should not be added as
        # pending for the client, therefore, ignore the client.
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


def _handle_abort_task(
        abort_task: Task
) -> Set[str]:
    """
    Removes the task being aborted from all clients currently executing it.
    The function does the following:
    1. Finds all tasks the abort task is aborting
    2. Finds all pending tasks that are to be aborted
    3. Sets these pending tasks status to aborted
    4. Stores the client IDs of all of these tasks that were aborted
    5. Moves the newly aborted tasks from the pending collection to the done
         collection
    6. Adds the abort task itself to the clients done tasks.
    7. Returns the client IDs of all clients that had at least one task aborted
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
        aborted_tasks = cast(
            list[ClientTask],
            _move_all(
                search_dict={
                    '_id.task_id': task_id
                },
                from_collection=DatabaseCollection.CLIENT_TASKS,
                to_collection=DatabaseCollection.CLIENT_DONE_TASKS,
                task_processor=lambda task: task.set_status(TaskStatus.ABORTED)
            )
        )

        for aborted_task in aborted_tasks:
            client_id = aborted_task.get_client_id()
            result_clients.add(client_id)

    # Return set of clients who had a task aborted
    return result_clients


def _move_all(
        search_dict: dict[str, Any],
        from_collection: DatabaseCollection,
        to_collection: DatabaseCollection,
        task_processor: Optional[Callable[[ClientTask], None]] = None
) -> Iterable[Deserializable]:
    """
    Moves all entries from one collection to another.
    :param search_dict: The search dict to use when searching for entries
    to move.
    :param from_collection: The collection to move entries from.
    :param to_collection: The collection to move entries to.
    :param task_processor: A function to process each task before it is
    moved.
    :return: An iterable of all the entries that were moved.
    """
    entries = controller.db.get_all(
        collection=from_collection,
        identifier=search_dict,
        entry_instance_creator=lambda: cast(
            Deserializable(),
            ClientTask()
        )
    )

    # For each task found, move it
    for entry in entries:
        if task_processor is not None:
            # Process the task if a processor was given
            task_processor(entry)

        # Add the task to the to_collection
        controller.db.set(
            collection=to_collection,
            entry_id=entry.id,
            entry=entry,
            overwrite=True
        )

        # Remove the task from the from_collection
        controller.db.delete(
            collection=from_collection,
            entry_id=entry.id
        )

        # Return the task
        yield entry


def _create_done_abort_task(abort_task: Task, client_id: str) -> ClientTask:
    """
    Creates a task that represents the abort task being executed on a client.
    Since the abort task is not actually executed on the client, this task
    is created as done.
    :param abort_task: The abort task, which specifies what task to abort.
    :param client_id: The ID of the client the abort task was intended to be
    executed on.
    :return: The created abort ClientTask
    """
    client_abort_task = ClientTask(
        client_id=client_id,
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

    return client_abort_task


def get_task_output():
    """
    Endpoint handling a tasks output given the tasks output or client id.
    :return: A list of task response.
    """
    auth = request.headers.get('Authorization')
    if auth != controller.settings.admin_key or auth is None:
        return '', 401

    client_id = request.args.get('id')
    task_id = request.args.get('task_id')

    key = {

    }

    # Wrong client id or bad formatting
    if client_id is not None and len(client_id) > 0:
        client_info = controller.db.get_client(
            client_id
        )

        if client_info is None:
            return 'Client does not exists', 404

        key['_id.client_id'] = client_id

    if task_id is not None and len(task_id) > 0:
        key['_id.task_id'] = task_id

    all_task_response = list(
        controller.db.get_all(
            collection=DatabaseCollection.CLIENT_TASK_RESPONSES,
            identifier=key,
            entry_instance_creator=cast(
                Deserializable,
                ClientTaskResponseCollection
            )
        ))

    return jsonify({
        'task_responses': [current_response.serialize()
                           for current_response in all_task_response]
    }), 200
