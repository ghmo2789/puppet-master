from control_server.src.crypto.client_id_generator import ClientIdGenerator
from control_server.src.database.database import Database
from control_server.src.database.database_builder import DatabaseBuilder
from control_server.src.database.mock_database import MockDatabase
from control_server.src.web_settings import WebSettings


class Controller:
    """
    A data class containing useful classes for the endpoints to use, such as the
    database, settings, etc.
    """
    def __init__(self):
        self._settings = WebSettings().read()
        self._db = DatabaseBuilder()\
            .set_mock(self._settings.mock_db)\
            .build()
        self._client_id_generator = ClientIdGenerator(
            self._settings.id_key
        )
        self._admin_key = self._settings.admin_key

        if isinstance(self._db, MockDatabase):
            print("Using mock database")

    @property
    def settings(self) -> WebSettings:
        return self._settings

    @property
    def client_id_generator(self) -> ClientIdGenerator:
        return self._client_id_generator

    @property
    def url_prefix(self) -> str:
        return self.settings.prefix

    @property
    def db(self) -> Database:
        return self._db


# Initialize controller and prefix once:
controller = Controller()
prefix = controller.url_prefix


def get_controller():
    """
    Gets the already initialized instance of the controller
    :return: The already initialized instance of the controller
    """
    return controller
