from typing import Dict

import pytest

from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.database.database import Database
from control_server.src.database.database_builder import DatabaseBuilder
from control_server.src.web_settings import WebSettings


class DatabaseTestData:
    def __init__(self):
        self.settings: WebSettings = WebSettings().read()
        self.db: Database = DatabaseBuilder() \
            .set_mock(self.settings.mock_db) \
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


@pytest.fixture
def mongo_test_data():
    data = DatabaseTestData()
    data.db.clear()
    yield data
    data.db.clear()


def test_set_delete_user(mongo_test_data: DatabaseTestData):
    """
    Tests that the set_user method works as expected without raising errors
    """
    db = mongo_test_data.db
    user = IdentifyingClientData(
        client_data=ClientData.load_from_dict(mongo_test_data.sample_user_data),
        ip=mongo_test_data.sample_ip
    )

    db.set_user(
        mongo_test_data.sample_id,
        user,
        overwrite=True
    )

    db.delete_user(
        mongo_test_data.sample_id
    )


def test_set_get_delete_get_user(mongo_test_data: DatabaseTestData):
    """
    Tests that the set_user method works as expected without raising errors,
    and that a set user can be retrieved
    """
    db = mongo_test_data.db
    user = IdentifyingClientData(
        client_data=ClientData.load_from_dict(mongo_test_data.sample_user_data),
        ip=mongo_test_data.sample_ip
    )

    db.set_user(
        mongo_test_data.sample_id,
        user,
        overwrite=True
    )

    retrieved_user = db.get_user(
        mongo_test_data.sample_id
    )

    assert retrieved_user is not None
    user.set_id(mongo_test_data.sample_id)
    assert_are_equal(user, retrieved_user)

    db.delete_user(
        mongo_test_data.sample_id
    )

    retrieved_user = db.get_user(
        mongo_test_data.sample_id
    )

    assert retrieved_user is None
