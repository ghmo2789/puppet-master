import pytest

from control_server.src import router

"""
This file contains fixtures that are used by multiple test files, and are set up
by pytest. 
"""


@pytest.fixture(scope="session", autouse=True)
def app():
    """
    Creates a test client for the app, and tears it down afterwards
    :return:
    """
    yield router.app

    if not router.router.controller.settings.mock_db:
        router.router.controller.db.clear()
