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
from control_server.src.database.database_collection import DatabaseCollection
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

    source_collection = DatabaseCollection.USER_TASKS if not done \
        else DatabaseCollection.USER_DONE_TASKS

    tasks = cast(
        List[ClientTask],
        list(controller.db.get_all(
            source_collection,
            identifier={
                "client_id": client_id.authorization
            },
            entry_instance_creator=lambda: cast(Deserializable, ClientTask())
        ))
    )

    if not done:
        for retrieved_task in tasks:
            controller.db.set(
                DatabaseCollection.USER_DONE_TASKS,
                entry_id=retrieved_task.id,
                entry=retrieved_task,
                overwrite=True
            )

            controller.db.delete(
                DatabaseCollection.USER_TASKS,
                entry_id=retrieved_task.id
            )

    return jsonify(
        [found_task.task.serialize() for found_task in tasks]
    ), 200


def task_response():
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

    client_response = ClientTaskResponse()
    if not client_response.load_from(
            lambda prop:
            request.json[prop] if prop in request.json else None,
            raise_error=False
    ):
        return "", 400

    identifying_response = ClientTaskResponseCollection(
        client_id=client_id.authorization,
        task_id=client_response.task_id
    )

    # Retrieve existing responses
    existing_response = cast(
        ClientTaskResponseCollection,
        controller.db.get_one(
            DatabaseCollection.USER_TASK_RESPONSES,
            identifier=identifying_response.id,
            entry_instance=cast(Deserializable, identifying_response)
        )
    )

    # If no responses were stored already, instantiate the variable
    if existing_response is None:
        existing_response = ClientTaskResponseCollection(
            client_id=client_id.authorization,
            task_id=client_response.task_id,
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
        DatabaseCollection.USER_TASK_RESPONSES,
        identifier=existing_response.id,
        entry=existing_response,
        overwrite=True
    )

    return "", 200
