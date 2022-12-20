from datetime import datetime
from typing import cast, List

from flask import request, jsonify

from control_server.src.data.anonymous_client_task_response import \
    AnonymousClientTaskResponse
from control_server.src.data.client_data import ClientData
from control_server.src.data.client_identifier import ClientIdentifier
from control_server.src.controller import controller
from control_server.src.data.client_task import ClientTask
from control_server.src.data.client_task_response import ClientTaskResponse
from control_server.src.data.client_task_response_collection import \
    ClientTaskResponseCollection
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.task_status import TaskStatus
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.utils.client_utils import seen_client
from control_server.src.utils.request_utils import get_ip
from control_server.src.utils.time_utils import time_now, time_now_str


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
    now = time_now_str()
    identifying_client_data = IdentifyingClientData(
        client_data=data,
        ip=client_ip,
        last_seen=now,
        first_seen=now
    )

    client_id = controller.client_id_generator.generate(identifying_client_data)

    if client_id is None:
        print(
            f"Failed to generate client id for client with IP "
            f"{request.remote_addr}."
        )
        return "", 500  # If unsuccessful, return 500 Internal Server Error

    client_id = str(client_id)

    existing_client = controller.db.get_client(
        client_id=client_id
    )

    identifying_client_data.first_seen = \
        (existing_client or identifying_client_data).first_seen or now

    controller.db.set_client(
        client_id=client_id,
        client=identifying_client_data,
        overwrite=True
    )

    # Update the client in the client tracker if there is a tracker
    if controller.client_tracker is not None:
        controller.client_tracker.mark_as_seen(
            client_id=client_id,
            polling_time=data.polling_time,
            is_newly_started=True
        )

    return jsonify(
        {
            'Authorization': client_id
        }
    ), 200


def task(done=False):
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

    if not seen_client(client_id.authorization):
        return "", 401

    source_collection = DatabaseCollection.CLIENT_TASKS if not done \
        else DatabaseCollection.CLIENT_DONE_TASKS

    tasks = cast(
        List[ClientTask],
        list(
            controller.db.get_all(
                source_collection,
                identifier={
                    "_id.client_id": client_id.authorization
                },
                entry_instance_creator=lambda: cast(
                    Deserializable,
                    ClientTask()
                )
            )
        )
    )

    serialized_result = [found_task.task.serialize() for found_task in tasks]

    if not done:
        for retrieved_task in tasks:
            retrieved_task.set_status(TaskStatus.IN_PROGRESS)
            controller.db.set(
                DatabaseCollection.CLIENT_DONE_TASKS,
                entry_id=retrieved_task.id,
                entry=retrieved_task,
                overwrite=True
            )

            controller.db.delete(
                DatabaseCollection.CLIENT_TASKS,
                entry_id=retrieved_task.id
            )

    return jsonify(
        serialized_result
    ), 200


def task_response():
    """
    Endpoint handing the client task response request, which stores the response
    in the database
    """
    client_id = ClientIdentifier()

    if not client_id.load_from(
            lambda prop:
            request.headers[prop] if prop in request.headers else None,
            raise_error=False
    ):
        return "", 400

    if not seen_client(client_id.authorization):
        return "", 401

    client_response = ClientTaskResponse()
    if not client_response.load_from(
            lambda prop:
            request.json[prop] if prop in request.json else None,
            raise_error=False,
            ignore_props={"time"}
    ):
        return "", 400

    client_response.time = time_now_str()

    task_key = {
        "_id.client_id": client_id.authorization,
        "_id.task_id": client_response.id
    }
    client_task = cast(
        ClientTask,
        controller.db.get_one(
            DatabaseCollection.CLIENT_DONE_TASKS,
            identifier=task_key,
            entry_instance=ClientTask()
        )
    )

    if client_task is None:
        return "Task does not exist", 404

    identifying_response = ClientTaskResponseCollection(
        client_id=client_id.authorization,
        task_id=client_response.id
    )

    # Retrieve existing responses
    existing_response = cast(
        ClientTaskResponseCollection,
        controller.db.get_one(
            DatabaseCollection.CLIENT_TASK_RESPONSES,
            entry_id=identifying_response.id,
            entry_instance=cast(Deserializable, identifying_response)
        )
    )

    # If no responses were stored already, instantiate the variable
    if existing_response is None:
        existing_response = ClientTaskResponseCollection(
            client_id=client_id.authorization,
            task_id=client_response.id,
            responses=[]
        )

    # Append newly received response to existing responses
    existing_response.responses.append(
        cast(
            AnonymousClientTaskResponse,
            client_response
        )
    )

    # Update responses in database
    controller.db.set(
        DatabaseCollection.CLIENT_TASK_RESPONSES,
        entry_id=existing_response.id,
        entry=existing_response,
        overwrite=True
    )

    client_task.set_status_code(client_response.status)
    controller.db.set(
        DatabaseCollection.CLIENT_DONE_TASKS,
        identifier=task_key,
        entry=client_task,
        overwrite=True,
        ignore_id=True
    )

    return "", 200
