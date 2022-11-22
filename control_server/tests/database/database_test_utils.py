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
    def __init__(self, use_mock: bool):
        self.settings: WebSettings = WebSettings().read()
        self.db: Database = DatabaseBuilder() \
            .set_mock(use_mock if not self.settings.mock_db else True) \
            .build()

        self.sample_user_data: Dict = {
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


def test_set_delete_user(test_data: DatabaseTestData):
    """
    Tests that the set_user method works as expected without raising errors
    """
    db = test_data.db
    user = IdentifyingClientData(
        client_data=ClientData.load_from_dict(test_data.sample_user_data),
        ip=test_data.sample_ip
    )

    db.set_user(
        test_data.sample_id,
        user,
        overwrite=True
    )

    db.delete_user(
        test_data.sample_id
    )


def test_set_get_all(test_data: DatabaseTestData):
    """
    Tests that the set_user method works as expected without raising errors,
    and that a set user can be retrieved
    """
    db = test_data.db
    users = [
        IdentifyingClientData(
            client_data=ClientData.load_from_dict(
                test_data.sample_user_data),
            ip=test_data.sample_ip
        ).set_id(test_data.sample_id + "1"),
        IdentifyingClientData(
            client_data=ClientData.load_from_dict(
                test_data.sample_user_data),
            ip=test_data.sample_ip + "2"
        ).set_id(test_data.sample_id + "2")
    ]

    for user in users:
        db.set_user(
            user.id,
            user,
            overwrite=True
        )

    retrieved_users = list(db.get_all(
        DatabaseCollection.USERS,
        {
            "client_data.os_name": test_data.sample_user_data["os_name"]
        },
        lambda: cast(Deserializable, IdentifyingClientData())
    ))

    assert len(retrieved_users) == len(users)
    assert all([user.id == retrieved_user.id for (user, retrieved_user) in
                zip(users, retrieved_users)])


def test_set_get_delete_get_user(test_data: DatabaseTestData):
    """
    Tests that the set_user method works as expected without raising errors,
    and that a set user can be retrieved
    """
    db = test_data.db
    user = IdentifyingClientData(
        client_data=ClientData.load_from_dict(test_data.sample_user_data),
        ip=test_data.sample_ip
    )

    db.set_user(
        test_data.sample_id,
        user,
        overwrite=True
    )

    retrieved_user = db.get_user(
        test_data.sample_id
    )

    assert retrieved_user is not None
    user.set_id(test_data.sample_id)
    assert_are_equal(user, retrieved_user)

    db.delete_user(
        test_data.sample_id
    )

    retrieved_user = db.get_user(
        test_data.sample_id
    )

    assert retrieved_user is None
