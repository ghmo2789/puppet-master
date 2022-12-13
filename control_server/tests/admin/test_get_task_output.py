import uuid

from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection


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


def set_task_response(client_id: str, task_id: str, db_collection: DatabaseCollection):
    """
    Helper function for setting task response in db.
    """
    pass

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
    assert response.status_code == 404


def test_task_output(client):
    """
    Test the /admin/taskouput endpoint
    """
    pass

