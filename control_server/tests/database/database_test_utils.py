from typing import Dict, cast

from control_server.src.data.client_data import ClientData
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.database.database import Database
from control_server.src.database.database_builder import DatabaseBuilder
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.web_settings import WebSettings


class DatabaseTestData:
    """
    Test class for database tests, containing useful dependencies, such as the
    database, settings and some sample data. The contents of the class are
    not mutated during the tests, so it can be reused (except for the databases
    contents).
    """

    def __init__(self, use_mock: bool):
        self.settings: WebSettings = WebSettings().read()
        self.db: Database = DatabaseBuilder() \
            .set_mock(use_mock if not self.settings.mock_db else True) \
            .build()

        self.sample_client_data: Dict = {
            "os_name": "test os",
            "os_version": "test os 1.0",
            "hostname": "host",
            "host_user": "user",
            "privileges": "admin"
        }

        self.sample_ip: str = "1.1.1.1"
        self.sample_id: str = "cba5f8a0-929e-4dd4-8b77-cfa907d65b9e"


def assert_are_equal(*args: IdentifyingClientData):
    """
    Asserts equality for base variables of two IdentifyingClientData objects,
    as well as for variables in the ClientData object contained within the
    IdentifyingClientData objects
    :param args: IdentifyingClientData objects to compare
    :return: Nothing.
    """
    dicts = [arg.serialize() for arg in args]

    compare_dicts = [
        dicts,
        [sub_dict["client_data"] for sub_dict in dicts]
    ]

    for dict_list in compare_dicts:
        keys = set.union(*[set(sub_dict.keys()) for sub_dict in dict_list])

        for key in keys:
            value = dict_list[0][key]

            for current_dict in dict_list:
                assert current_dict[key] == value


def test_set_delete_client(test_data: DatabaseTestData):
    """
    Tests that the set_client method works as expected without raising errors
    """
    db = test_data.db
    client = IdentifyingClientData(
        client_data=ClientData.load_from_dict(test_data.sample_client_data),
        ip=test_data.sample_ip
    )

    db.set_client(
        test_data.sample_id,
        client,
        overwrite=True
    )

    db.delete_client(
        test_data.sample_id
    )


def test_set_get_all(test_data: DatabaseTestData):
    """
    Tests that the set_client method works as expected without raising errors,
    and that a set client can be retrieved
    """
    db = test_data.db
    clients = [
        IdentifyingClientData(
            client_data=ClientData.load_from_dict(
                test_data.sample_client_data
            ),
            ip=test_data.sample_ip
        ).set_id(test_data.sample_id + "1"),
        IdentifyingClientData(
            client_data=ClientData.load_from_dict(
                test_data.sample_client_data
            ),
            ip=test_data.sample_ip + "2"
        ).set_id(test_data.sample_id + "2")
    ]

    for client in clients:
        db.set_client(
            client.id,
            client,
            overwrite=True
        )

    retrieved_clients = list(
        db.get_all(
            DatabaseCollection.CLIENTS,
            {
                "client_data.os_name": test_data.sample_client_data["os_name"]
            },
            lambda: cast(Deserializable, IdentifyingClientData())
        )
    )

    assert len(retrieved_clients) == len(clients)
    assert all([
        client.id == retrieved_client.id
        for (client, retrieved_client) in zip(clients, retrieved_clients)
    ])


def test_set_get_delete_get_client(test_data: DatabaseTestData):
    """
    Tests that the set_client method works as expected without raising errors,
    and that a set client can be retrieved
    """
    db = test_data.db
    client = IdentifyingClientData(
        client_data=ClientData.load_from_dict(test_data.sample_client_data),
        ip=test_data.sample_ip
    )

    db.set_client(
        test_data.sample_id,
        client,
        overwrite=True
    )

    retrieved_client = db.get_client(
        test_data.sample_id
    )

    assert retrieved_client is not None
    client.set_id(test_data.sample_id)
    assert_are_equal(client, retrieved_client)

    db.delete_client(
        test_data.sample_id
    )

    retrieved_client = db.get_client(
        test_data.sample_id
    )

    assert retrieved_client is None
