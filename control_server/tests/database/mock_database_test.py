import pytest

from control_server.tests.database.database_test_utils import DatabaseTestData
from control_server.tests.database import database_test_utils


@pytest.fixture
def mongo_test_data():
    """
    Set up testing data, and tear down afterwards
    :return: Nothing.
    """
    data = DatabaseTestData(use_mock=True)
    data.db.clear()
    yield data
    data.db.clear()


def test_set_delete_client(mongo_test_data: DatabaseTestData):
    """
    Tests that the set_client method works as expected without raising errors
    """
    database_test_utils.test_set_delete_client(test_data=mongo_test_data)


def test_set_get_all(mongo_test_data: DatabaseTestData):
    """
    Tests that the set_client method works as expected without raising errors,
    and that a set client can be retrieved
    """
    database_test_utils.test_set_get_all(test_data=mongo_test_data)


def test_set_get_delete_get_client(mongo_test_data: DatabaseTestData):
    """
    Tests that the set_client method works as expected without raising errors,
    and that a set client can be retrieved
    """
    database_test_utils.test_set_get_delete_get_client(test_data=mongo_test_data)
