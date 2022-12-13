import uuid
from typing import cast

from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.client_task_response import ClientTaskResponse
from control_server.src.data.client_task_response_collection import ClientTaskResponseCollection
from control_server.src.data.identifying_client_data import IdentifyingClientData
from control_server.src.data.client_data import ClientData
from control_server.src.data.anonymous_client_task_response import AnonymousClientTaskResponse


def randomize_ids() -> (str, str):
    """
    Randomizes the client and task IDs. Useful to prevent key collisions in
    database during testing. UUIDs are 128-bits, so the chance of collision by
    generating the same IDs twice is negligible.
    :return: two str containing random numbers
    """

    client_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    return client_id, task_id


def set_task_response(client_id: str, task_id: str):
    """
    Helper function for setting task response in db.
    """
    # Create a client and save it in the DB
    client = {
        "os_name": "2",
        "os_version": "2",
        "hostname": "2",
        "host_user": "2",
        "privileges": "2",
    }
    client_ip = str(uuid.uuid4())
    data = ClientData.load_from_dict(client, raise_error=True)
    new_client = IdentifyingClientData(
        client_data=data,
        ip=client_ip
    )
    new_client.set_id(client_id)
    controller.db.set_client(
        client_id=client_id,
        client=new_client,
        overwrite=True
    )

    # Creat a task response
    client_response = ClientTaskResponse(
        task_id=task_id,
        result="hello Uppsala",
        status=0
    )

    # Create a client task response and insert in the DB
    client_task_response = ClientTaskResponseCollection(
        client_id=client_id,
        task_id=task_id,
        responses=[],
    )
    client_task_response.responses.append(
        cast(
            AnonymousClientTaskResponse,
            client_response
        )
    )

    controller.db.set(
        collection=DatabaseCollection.CLIENT_TASK_RESPONSES,
        entry_id=client_task_response.id,
        entry=client_task_response,
        overwrite=True

    )


def test_task_output_invalid_authorization(client):
    """
    Test the /admin/taskoutput endpoint with missing authorization key.
    :param client:
    """
    response = client.get(f"{get_prefix()}/admin/taskoutput", headers={

    })

    assert response.status_code == 401, "Received a non-401 status code"


def test_task_output_wrong_client_id(client):
    """
    Test the /admin/taskoutput endpoint with wrong client id
    :param client:
    """
    response = client.get(f"{get_prefix()}/admin/taskoutput", headers={
        "Authorization": controller.settings.admin_key
    }, query_string={
        "id": "1234",
        "task_id": "1234"
    })
    assert response.status_code == 404, "Received a non-404 status code"


def test_task_output(client):
    """
    Test the /admin/taskouput endpoint
    """
    client_id, task_id = randomize_ids()
    set_task_response(
        client_id=client_id,
        task_id=task_id,
    )

    response = client.get(f"{get_prefix()}/admin/taskoutput", headers={
        "Authorization": controller.settings.admin_key
    }, query_string={
        "id": client_id,
        "task_id": task_id
    })
    task_response = response.json.get("task_responses")[0]
    # task_response_db = ClientTaskResponseCollection().deserialize(task_response[0])
    # print(task_response_db)
    assert response.status_code == 200, "Received a non-200 status code"
    assert task_response["_id"].get("task_id") == task_id, "Task ID does not match"
    assert task_response["_id"].get("client_id") == client_id, "Client ID does not match"
    assert task_response["responses"][0].get("status") == 0, "Status code does not match"
    assert task_response["responses"][0].get("id") == task_id, "Task ID does not match"

