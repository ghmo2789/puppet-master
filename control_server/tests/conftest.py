import pytest

from control_server.src import router
from control_server.src.middleware.compression.static_compression_method \
    import StaticCompressionMethod
from control_server.src.middleware.obfuscation_key import ObfuscationKey

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
    # Disable compression for testing. Is enabled explicitly for individual
    # tests if needed.
    StaticCompressionMethod(
        method=None
    ).set()

    # Do the same for obfuscation
    ObfuscationKey.static_key = None

    router.init()
    yield router.app

    if not router.router.controller.settings.mock_db:
        router.router.controller.db.clear()
