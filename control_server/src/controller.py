from control_server.src.database.database import Database
from control_server.src.database.database_builder import DatabaseBuilder
from control_server.src.database.mock_database import MockDatabase
from control_server.src.web_settings import WebSettings


class Controller:
    def __init__(self):
        self._settings = WebSettings().read()
        self._db = DatabaseBuilder()\
            .set_mock(self._settings.mock_db)\
            .build()

        if isinstance(self._db, MockDatabase):
            print("Using mock database")

    @property
    def settings(self) -> WebSettings:
        return self._settings

    @property
    def url_prefix(self) -> str:
        return self.settings.prefix

    @property
    def db(self) -> Database:
        return self._db


controller = Controller()
prefix = controller.url_prefix


def get_controller():
    return controller
