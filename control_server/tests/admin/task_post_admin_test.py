import uuid
from typing import cast

from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import IdentifyingClientData
from control_server.src.data.task_status import TaskStatus
from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.client_task import ClientTask
from control_server.src.data.task import Task


def randomize_ids() -> (str, str):
    """
    TODO: Add comment here
    """
    client_id = str(uuid.uuid4())
    client_ip = str(uuid.uuid4())
    return client_id, client_ip


def set_client(client_id: str, client_ip: str):
    """
    Helper function for setting a client in the database
    """
    client_1 = {
        "os_name": "2",
        "os_version": "2",
        "hostname": "2",
        "host_user": "2",
        "privileges": "2",
    }
    client_data = ClientData.load_from_dict(client_1, raise_error=True)
    new_client = IdentifyingClientData(
        client_data=client_data,
        ip=client_ip
    )
    new_client.set_id(client_id)
    controller.db.set_user(
        user_id=client_id,
        user=new_client,
        overwrite=True
    )


def test_post_invalid_authorization(client):
    """
    Test the /admin/task post endpoint with missing authorization
    :param client:
    :return:
    """
    response = client.post(f"{get_prefix()}/admin/task", json={

    })
    assert response.status_code == 401, \
        "Received a non-401 status code"


def test_post_task_wrong_client_id(client):
    """
    Test the /admin/task post endpoint with wrong client id
    :param client:
    :return:
    """
    response_missing_client_id = client.post(f"{get_prefix()}/admin/task", headers={
        "Authorization": controller.settings.admin_key
    }, json={

    })

    response_wrong_client_id = client.post(f"{get_prefix()}/admin/task", headers={
        "Authorization": controller.settings.admin_key
    }, json={
        "client_id": "1234",
        "data": "test",
        "name": "test",
        "min_delay": "0",
        "max_delay": "0"
    })
    assert response_missing_client_id.status_code == 400, \
        "Received a non-400 status code"
    assert response_wrong_client_id == 404, \
        "Received a non-404 status code"


def test_post_task_missing_task(client):
    """
    Test the /admin/task post endpoint with missing task
    :param client:
    :return:
    """
    response_missing_task = client.post(f"{get_prefix()}/admin/task", headers={
        "Authorization": controller.settings.admin_key
    }, json={
        "client_id": "1234"
    })
    assert response_missing_task.status_code == 400, \
        "Received a non-404 status code"


def test_post_task(client):
    """
    Test the /admin/task post endpoint
    :param client:
    :return:
    """
    # Set client in DB
    client_id, client_ip = randomize_ids()
    set_client(client_id=client_id, client_ip=client_ip)

    response = client.post(f"{get_prefix()}/admin/task", headers={
        "Authorization": controller.settings.admin_key
    }, json={
        "client_id": client_id,
        "data": "test",
        "name": "test",
        "min_delay": "0",
        "max_delay": "0"
    })

    task_id = response.get_data(as_text=True)
    client_task = cast(
        ClientTask,
        controller.db.get_one(
            collection=DatabaseCollection.USER_TASKS,
            identifier={
                "_id.task_id": task_id
            },
            entry_instance=ClientTask()
        )
    )
    assert response.status_code == 200, \
        "Received a non-200 status code"
    assert client_task.id.get("task_id") == task_id
    assert client_task.id.get("client_id") == client_id
    assert client_task.status_code == -2
    assert client_task.status == TaskStatus.PENDING

