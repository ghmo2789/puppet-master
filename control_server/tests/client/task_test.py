import uuid

from control_server.src.controller import controller
from control_server.src.data.client_task import ClientTask
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.task import Task
from control_server.src.database.database_collection import DatabaseCollection
from control_server.tests.utils.generic_test_utils import get_prefix


def test_task_invalid_id(client):
    """
    Test the client task endpoint with an invalid client id/Authorization header
    :param client:
    :return:
    """
    response = client.get(f"{get_prefix()}/client/task", headers={

    })

    assert response.status_code == 400


def test_task(client):
    """
    Test the client task endpoint with a valid client id/Authorization header
    :param client:
    :return:
    """
    client_id = "1966283-b9b8-4502-a431-6bc39046481f"
    task = Task("test", "test", 0, 0).with_id()
    client_task = ClientTask(
        client_id=client_id,
        task_id=task.id,
        task=task
    )

    controller.db.set(
        collection=DatabaseCollection.CLIENTS,
        entry_id=client_id,
        entry=IdentifyingClientData(),
        overwrite=True
    )

    controller.db.set(
        collection=DatabaseCollection.CLIENT_TASKS,
        entry_id=client_task.id,
        entry=client_task,
        overwrite=True
    )

    response = client.get(f"{get_prefix()}/client/task", headers={
        "Authorization": client_id
    })

    empty_response = client.get(f"{get_prefix()}/client/task", headers={
        "Authorization": client_id
    })

    done_response = client.get(
        f"{get_prefix()}/client/task",
        headers={
            "Authorization": client_id
        },
        query_string={
            "done": True
        }
    )

    tasks = [
                Task().deserialize(task) for task in response.json
            ] + [
                Task().deserialize(task) for task in done_response.json
            ]

    assert response.status_code == 200
    assert len(tasks) == 1
    assert len(empty_response.json) == 0

    for response_task in tasks:
        assert response_task is not None
        assert response_task.id == client_task.get_task_id()

        assert response_task.name == task.name
        assert response_task.data == task.data
        assert response_task.min_delay == task.min_delay
        assert response_task.max_delay == task.max_delay


def test_task_last_seen(client):
    """
    Tests that requesting tasks from the server updates the last_seen property
    of the client in the database.
    :param client:
    :return:
    """
    client_id = str(uuid.uuid4())

    controller.db.set(
        collection=DatabaseCollection.CLIENTS,
        entry_id=client_id,
        entry=IdentifyingClientData(),
        overwrite=True
    )

    pre_client = controller.db.get_client(
        client_id=client_id
    )

    response = client.get(f"{get_prefix()}/client/task", headers={
        "Authorization": client_id
    })

    post_client = controller.db.get_client(
        client_id=client_id
    )

    assert response.status_code == 200
    assert pre_client.last_seen is None
    assert post_client.last_seen is not None
