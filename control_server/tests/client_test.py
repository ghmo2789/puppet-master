from typing import List

import pytest

from control_server.src.data.client_task_collection import ClientTaskCollection
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
    tasks = [
        Task("test", "test", 0, 0).with_id()
    ]

    controller.db.set(
        DatabaseCollection.USER_TASKS,
        client_id,
        ClientTaskCollection(
            client_id=client_id,
            tasks=tasks
        ),
        overwrite=True
    )

    response = client.get(f"{get_prefix()}/client/task", headers={
        "Authorization": client_id
    })

    response_task_collection = ClientTaskCollection()
    response_task_collection.deserialize(response.json)

    assert response.status_code == 200
    assert response_task_collection is not None
    assert response_task_collection.client_id == client_id
    received_task = response_task_collection.tasks[0]
    assert len(response_task_collection.tasks) == len(tasks)

    assert response_task_collection.tasks[0].name == tasks[0].name
    assert response_task_collection.tasks[0].data == tasks[0].data
    assert response_task_collection.tasks[0].min_delay == tasks[0].min_delay
    assert response_task_collection.tasks[0].max_delay == tasks[0].max_delay

