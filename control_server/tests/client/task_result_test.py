import uuid
from typing import cast

from control_server.src.controller import controller
from control_server.src.data.client_task_response import ClientTaskResponse
from control_server.src.data.client_task_response_collection import \
    ClientTaskResponseCollection
from control_server.src.data.deserializable import Deserializable
from control_server.src.database.database_collection import DatabaseCollection
from control_server.tests.utils.generic_test_utils import get_prefix

client_id = "1966283-b9b8-4503-a431-6bc39046481f"
task_id = "1966284-b9b8-4543-a431-6bc39046481f"


def randomize_ids():
    global client_id, task_id
    client_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())


def get_task_response():
    return ClientTaskResponse(
        task_id=task_id,
        result="success",
        status=0
    )


def assert_no_responses():
    existing = list(controller.db.get_all(
        collection=DatabaseCollection.USER_TASK_RESPONSES,
        identifier={
            "client_id": client_id,
            "task_id": task_id
        },
        entry_instance_creator=cast(
            Deserializable,
            ClientTaskResponseCollection
        )
    ))

    assert len(existing) == 0, "Existing responses found"
    return existing


def get_responses() -> ClientTaskResponseCollection:
    return cast(
        ClientTaskResponseCollection,
        controller.db.get_one(
            collection=DatabaseCollection.USER_TASK_RESPONSES,
            identifier={
                "client_id": client_id,
                "task_id": task_id
            },
            entry_instance=cast(
                Deserializable,
                ClientTaskResponseCollection()
            )
        )
    )


def test_task_response(client):
    """
    Test the client task response endpoint to ensure posted task responses are
    saved to database
    :param client:
    :return:
    """
    randomize_ids()
    assert_no_responses()
    task_response = get_task_response()

    response = client.post(
        f"{get_prefix()}/client/task/response",
        headers={
            "Authorization": client_id
        },
        json=task_response.serialize()
    )

    collection = get_responses()

    assert response.status_code == 200, "Received non-200 status code"
    assert collection.client_id == client_id, "Client ID does not match"

    assert collection.responses[-1].result == task_response.result, \
        "Incorrect result for response"
    assert collection.responses[-1].status == task_response.status, \
        "Incorrect status for response"


def test_task_two_responses(client):
    """
    Test the client task response endpoint to ensure posted task responses are
    saved to database, in order
    :param client:
    :return:
    """
    randomize_ids()
    assert_no_responses()
    number = 10

    task_responses = [ClientTaskResponse(
        task_id=task_id,
        result=f"success_{index}",
        status=index
    ) for index in range(number)]

    for current_response in task_responses:
        response = client.post(
            f"{get_prefix()}/client/task/response",
            headers={
                "Authorization": client_id
            },
            json=current_response.serialize()
        )

        assert response.status_code == 200, "Received non-200 status code"

    collection = get_responses()
    assert len(collection.responses) == number, "Incorrect number of responses"
    assert collection.client_id == client_id, "Client ID does not match"

    for index in range(number):
        assert \
            collection.responses[index].result == \
            task_responses[index].result, \
            f"Incorrect result for response {index}"

        assert \
            collection.responses[index].status == \
            task_responses[index].status, \
            f"Incorrect status for response {index}"
