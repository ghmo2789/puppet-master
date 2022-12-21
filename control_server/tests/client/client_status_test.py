import time
import uuid
from typing import Tuple, Any

from control_server.src.client.client_status import ClientStatus
from control_server.src.controller import controller
from control_server.src.data.client_identifier import ClientIdentifier
from control_server.src.utils.time_utils import time_now
from control_server.tests.utils.generic_test_utils import get_prefix

sample_client = {
    "os_name": "1",
    "os_version": "1",
    "hostname": "1",
    "host_user": "1",
    "privileges": "1",
    "host_id": None,
    "polling_time": 0.1  # If DB latency is high, this may need to be increased
    # for tests to pass
}


def generate_ids(sample_client_data: dict[str, Any] = None) -> Tuple[str, str]:
    """
    Generates a random client and task ID
    :return:
    """
    if sample_client_data is not None:
        sample_client_data['host_id'] = str(uuid.uuid4())

    return str(uuid.uuid4()), str(uuid.uuid4())


def init_client(
        client,
        client_data: dict[str, Any] = None
) -> Tuple[str, dict[str, Any]]:
    """
    Initializes a client and returns its ID
    :return:
    """
    if client_data is None:
        client_data = sample_client.copy()
        _ = generate_ids(sample_client_data=client_data)

    response = client.post(
        f"{get_prefix()}/client/init",
        json=client_data
    )

    assert response.status_code == 200, \
        f"Expected 200 OK status code, got {response.status_code}"

    client_id = ClientIdentifier()

    assert client_id.load_from(
        lambda prop:
        response.json[prop.title()] if prop.title() in response.json else None,
        raise_error=False
    ), "Failed to load client ID, is the received data valid?"

    return client_id.authorization, client_data


def poll(client, client_id: str):
    """
    Polls the client
    :param client: Pytest-Flask client to use
    :param client_id: Client ID to poll
    :return: Nothing
    """
    response = client.get(
        f"{get_prefix()}/client/task",
        headers={
            "Authorization": client_id
        }
    )

    assert response.status_code == 200, \
        f"Expected 200 OK status code, got {response.status_code}"


def test_init_status(client):
    """
    Test the client init endpoint with a valid request using test data.
    :param client:
    :return:
    """
    client_id, client_data = init_client(client)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.STARTED
    )


def test_init_poll_status(client):
    """
    Test the client init endpoint with a valid request using test data.
    :param client:
    :return:
    """
    client_id, client_data = init_client(client)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.STARTED
    )

    poll(client, client_id=client_id)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.ACTIVE
    )


def test_init_poll_inactive_status(client):
    """
    Test the client init endpoint with a valid request using test data.
    :param client:
    :return:
    """
    client_id, client_data = init_client(client)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.STARTED
    )

    poll(client, client_id=client_id)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.ACTIVE
    )

    do_tracker_update(client_data=client_data)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.INACTIVE
    )

    poll(client, client_id=client_id)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.ACTIVE
    )


def test_init_poll_inactive_init_status(client):
    """
    Test the client init endpoint with a valid request using test data.
    :param client:
    :return:
    """
    client_id, client_data = init_client(client)
    poll(client, client_id=client_id)

    do_tracker_update(client_data=client_data)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.INACTIVE
    )

    init_client(client, client_data=client_data)

    _assert_online_status(
        client_id=client_id,
        expected_status=ClientStatus.STARTED
    )


def do_tracker_update(client_data: dict[str, Any]):
    time.sleep(client_data['polling_time'] * 2.5)
    assert controller.client_tracker.update(timeout=10), \
        "Client tracker update failed"


def _assert_online_status(
        client_id: str,
        expected_status: ClientStatus
):
    """
    Asserts the online status of a client
    :param client_id: The id of the client
    :param expected_status: The expected status
    :return:
    """
    actual_status = controller.client_tracker.get_status(
        client_id=client_id
    )

    assert actual_status == expected_status
