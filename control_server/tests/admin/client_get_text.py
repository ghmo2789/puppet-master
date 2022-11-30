from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import IdentifyingClientData


def test_client_invalid_authorization(client):
    """
    Test the /admin/client endpoint with missing authorization key.
    """
    response = client.get(f"{get_prefix()}/admin/client", headers={

    })
    assert response.status_code == 401


def test_client_missing_id(client):
    """
    Test the /admin/client endpoint with missing client id
    """
    response = client.get(f"{get_prefix()}/admin/client", headers={
        "Authorization": controller.settings.admin_key
    })

    assert response.status_code == 400


def test_client_invalid_id(client):
    """
    Test the /admin/client endpoint with wrong client id
    """
    response = client.get(f"{get_prefix()}/admin/client?id=1234", headers={
       "Authorization": controller.settings.admin_key
    })

    assert response.status_code == 404


def test_client(client):
    """
    The the /admin/client endpoint, with a valid client id and client
    """
    new_client = {
        "os_name": "1",
        "os_version": "1",
        "hostname": "1",
        "host_user": "1",
        "privileges": "1",
    }
    client_id = "1966283-b9b8-4503-a431-6bc39046481f"
    data = ClientData.load_from_dict(new_client, raise_error=True)
    new_user = IdentifyingClientData(
        client_data=data,
        ip=client_id,
    )

    controller.db.set_user(
        user_id=client_id,
        user=new_user,
        overwrite=True
    )

    response = client.get(f"{get_prefix()}/admin/client", headers={
        "Authorization": controller.settings.admin_key
    }, query_string={
        "id": client_id
    })

    assert response.status_code == 200
    assert response.json.get("_id") == client_id




