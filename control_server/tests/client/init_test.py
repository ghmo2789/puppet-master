from datetime import datetime

from control_server.src.controller import controller
from control_server.src.utils.time_utils import time_now
from control_server.tests.utils.generic_test_utils import get_prefix


def test_init(client):
    """
    Test the client init endpoint with a valid request using test data.
    :param client:
    :return:
    """
    response = client.post(
        f"{get_prefix()}/client/init", json={
            "os_name": "1",
            "os_version": "1",
            "hostname": "1",
            "host_user": "1",
            "privileges": "1",
            "host_id": "1",
            "polling_time": 1
        }
    )

    assert response.status_code == 200
    client_id = response.json['Authorization']

    client_data = controller.db.get_client(
        client_id=client_id
    )

    assert client_data is not None

    now = time_now()
    assert client_data.get_first_seen() < now
    assert client_data.get_last_seen() < now
    assert client_data.get_first_seen() <= client_data.get_last_seen()


def test_init_twice(client):
    """
    Test the client init endpoint with a valid request using test data.
    :param client:
    :return:
    """
    response = client.post(
        f"{get_prefix()}/client/init", json={
            "os_name": "1",
            "os_version": "1",
            "hostname": "1",
            "host_user": "1",
            "privileges": "1",
            "host_id": "1",
            "polling_time": 1
        }
    )

    assert response.status_code == 200
    initial_client_id = response.json['Authorization']

    response = client.post(
        f"{get_prefix()}/client/init", json={
            "os_name": "1",
            "os_version": "1",
            "hostname": "1",
            "host_user": "1",
            "privileges": "1",
            "host_id": "1",
            "polling_time": 1
        }
    )

    assert response.status_code == 200
    client_id = response.json['Authorization']

    assert initial_client_id == client_id

    client_data = controller.db.get_client(
        client_id=client_id
    )

    assert client_data is not None

    now = time_now()
    assert client_data.get_first_seen() < now
    assert client_data.get_last_seen() < now
    assert client_data.get_first_seen() < client_data.get_last_seen()
