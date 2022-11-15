from typing import List

import pytest

from control_server.tests.utils import get_prefix
from control_server.src import router


@pytest.fixture
def app():
    return router.app


def test_init(client):
    response = client.post(f"{get_prefix()}/client/init", json={
        "os_name": "1",
        "os_version": "1",
        "hostname": "1",
        "host_user": "1",
        "privileges": "1"
    })

    assert response.status_code == 200

def test_task_invalid_id(client):
    response = client.get(f"{get_prefix()}/client/task", headers={

    })

    assert response.status_code == 400

def test_task(client):
    response = client.get(f"{get_prefix()}/client/task", headers={
        "Authorization": "1969283-b9b8-4502-a431-6bc39046481f"
    })

    assert isinstance(response.json, List)
    assert response.status_code == 200
