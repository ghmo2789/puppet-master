from typing import List

import pytest

from control_server.src.data.client_task import ClientTask
from control_server.src.data.task import Task
from control_server.src.database.database_collection import DatabaseCollection
from control_server.tests.utils import get_prefix
from control_server.src import router
from control_server.src.controller import controller


@pytest.fixture
def app():
    yield router.app

    if not router.router.controller.settings.mock_db:
        router.router.controller.db.clear()


def test_init(client):
    """
    Test the client init endpoint with a valid request using test data.
    :param client:
    :return:
    """
    response = client.post(f"{get_prefix()}/client/init", json={
        "os_name": "1",
        "os_version": "1",
        "hostname": "1",
        "host_user": "1",
        "privileges": "1"
    })

    assert response.status_code == 200


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
        task_id=task.task_id,
        task=task
    )

    tasks = [
        client_task
    ]

    controller.db.set(
        DatabaseCollection.USER_TASKS,
        client_task.id,
        client_task,
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
        ClientTask().deserialize(task) for task in response.json
    ] + [
        ClientTask().deserialize(task) for task in done_response.json
    ]

    assert response.status_code == 200
    assert len(tasks) == 1
    assert len(empty_response.json) == 0

    for response_task in tasks:
        assert response_task is not None
        assert response_task.client_id == client_task.client_id
        assert response_task.task_id == client_task.task_id

        assert response_task.task.name == task.name
        assert response_task.task.data == task.data
        assert response_task.task.min_delay == task.min_delay
        assert response_task.task.max_delay == task.max_delay
