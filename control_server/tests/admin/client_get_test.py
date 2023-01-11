import uuid

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
    assert response.status_code == 401, "Received a non-401 status code"


def test_client_missing_id(client):
    """
    Test the /admin/client endpoint with missing client id
    """
    response = client.get(f"{get_prefix()}/admin/client", headers={
        "Authorization": controller.settings.admin_key
    })

    assert response.status_code == 400, "Received a non-400 status code"


def test_client_invalid_id(client):
    """
    Test the /admin/client endpoint with wrong client id
    """
    response = client.get(f"{get_prefix()}/admin/client?id=1234", headers={
       "Authorization": controller.settings.admin_key
    })

    assert response.status_code == 404, "Received a non-404 status code"


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
        "host_id": "1",
        "polling_time": 1
    }
    client_id = str(uuid.uuid4())
    client_ip = str(uuid.uuid4())

    data = ClientData.load_from_dict(new_client, raise_error=True)
    new_client = IdentifyingClientData(
        client_data=data,
        ip=client_ip
    )
    new_client.set_id(client_id)

    controller.db.set_client(
        client_id=client_id,
        client=new_client,
        overwrite=True
    )

    response = client.get(f"{get_prefix()}/admin/client", headers={
        "Authorization": controller.settings.admin_key
    }, query_string={
        "id": client_id
    })
    response_client = IdentifyingClientData().deserialize(response.json)

    assert response.status_code == 200, "Received a non-200 status code"
    assert response_client.id == client_id, "Client ID does not match"




