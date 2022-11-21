from control_server.tests.utils import get_prefix


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
