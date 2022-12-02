from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import IdentifyingClientData


def test_all_client_invalid_authorization(client):
    """
    Test the /admin/allclients endpoint with missing authorization key.
    :param client:
    :return:
    """
    response = client.get(f"{get_prefix()}/admin/allclients", headers={

    })
    assert response.status_code == 401


def test_all_client_no_clients(client):
    """
    Test the /admin/allclients endpoint with no clients in the DB.
    :param client:
    :return:
    """
    response = client.get(f"{get_prefix()}/admin/allclients", headers={
        "Authorization": controller.settings.admin_key
    })

    assert response.status_code == 404


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

    client_1_id = "1966283-b9b8-4503-a431-6bc39046481e"
    client_2_id = "1966283-b9b8-4503-a431-6bc39046481g"

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

    controller.db.set_user(
        user_id=client_1_id,
        user=new_client_1,
        overwrite=True,
    )
    controller.db.set_user(
        user_id=client_2_id,
        user=new_client_2,
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

    assert response.status_code == 200
    assert len(all_clients) == 2

    for i in range(len(all_clients)):
        assert all_clients[i].id == new_clients[i].id
        assert all_clients[i].ip == new_clients[i].ip
        assert all_clients[i].client_data.get("host_user") \
               == new_clients[i].client_data.host_user
        assert all_clients[i].client_data.get("hostname")\
               == new_clients[i].client_data.hostname
        assert all_clients[i].client_data.get("os_name") \
               == new_clients[i].client_data.os_name
        assert all_clients[i].client_data.get("os_version")\
               == new_clients[i].client_data.os_version
        assert all_clients[i].client_data.get("privileges") \
               == new_clients[i].client_data.privileges
