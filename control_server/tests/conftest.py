import pytest

from control_server.src import router


@pytest.fixture(scope="session", autouse=True)
def app():
    yield router.app

    if not router.router.controller.settings.mock_db:
        router.router.controller.db.clear()
