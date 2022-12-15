import uuid

from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import IdentifyingClientData


def randomize_ids() -> (str, str):
    """
        Randomizes the client and task IDs. Useful to prevent key collisions in
        database during testing. UUIDs are 128-bits, so the chance of collision by
        generating the same IDs twice is negligible.
        :return:
        """
    client_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    return client_id, task_id


def test_all_client_invalid_authorization(client):
    """
    Test the /admin/allclients endpoint with missing authorization key.
    :param client:
    :return:
    """
    response = client.get(f"{get_prefix()}/admin/allclients", headers={

    })
    assert response.status_code == 401, "Received a non-401 status code"


def test_all_client_no_clients(client):
    """
    Test the /admin/allclients endpoint with no clients in the DB.
    :param client:
    :return:
    """
    response = client.get(f"{get_prefix()}/admin/allclients", headers={
        "Authorization": controller.settings.admin_key
    })

    assert response.status_code == 404, "Received a non-404 status code"


def test_all_client_with_clients(client):
    """
    Test the /admin/allclients endpoint with clients in DB.
    :param client:
    :return:
    """
    client_1 = {
        "os_name": "1",
        "os_version": "1",
        "hostname": "1",
        "host_user": "1",
        "privileges": "1",
    }

    client_2 = {
        "os_name": "1",
        "os_version": "1",
        "hostname": "1",
        "host_user": "1",
        "privileges": "1",
    }

    client_1_id, task_1_id = randomize_ids()
    client_2_id, task_2_id = randomize_ids()

    data_1 = ClientData.load_from_dict(client_1, raise_error=True)
    data_2 = ClientData.load_from_dict(client_2, raise_error=True)

    new_client_1 = IdentifyingClientData(
        client_data=data_1,
        ip=client_1_id,
    )
    new_client_2 = IdentifyingClientData(
        client_data=data_2,
        ip=client_2_id
    )

    new_client_1.set_id(client_1_id)
    new_client_2.set_id(client_2_id)

    controller.db.set_client(
        client_id=client_1_id,
        client=new_client_1,
        overwrite=True,
    )
    controller.db.set_client(
        client_id=client_2_id,
        client=new_client_2,
        overwrite=True
    )

    new_clients = [new_client_1, new_client_2]

    response = client.get(f"{get_prefix()}/admin/allclients", headers={
        "Authorization": controller.settings.admin_key
    })

    all_clients = [
        IdentifyingClientData().deserialize(cur_client)
        for cur_client in response.json["all_clients"]
    ]

    assert response.status_code == 200, "Received a non-200 status code"
    assert len(all_clients) == 2, "Incorrect number of clients"

    for i in range(len(all_clients)):
        assert all_clients[i].id == new_clients[i].id, "client ID does not match"
        assert all_clients[i].ip == new_clients[i].ip, "client IP does not match"
        assert all_clients[i].client_data.get("host_user") \
               == new_clients[i].client_data.host_user, "Client name does not match"
        assert all_clients[i].client_data.get("hostname")\
               == new_clients[i].client_data.hostname, "Client username does not match"
        assert all_clients[i].client_data.get("os_name") \
               == new_clients[i].client_data.os_name, "Client OS does not match"
        assert all_clients[i].client_data.get("os_version")\
               == new_clients[i].client_data.os_version, "Client Os version does not match"
        assert all_clients[i].client_data.get("privileges") \
               == new_clients[i].client_data.privileges, "Client privileges does not match"
