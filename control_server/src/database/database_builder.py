from control_server.src.database.database import Database
from control_server.src.database.mock_database import MockDatabase
from control_server.src.database.mongo_database import MongoDatabase


class DatabaseBuilder:
    def __init__(self):
        self._is_mock = False

    def set_mock(self, is_mock: bool):
        self._is_mock = is_mock
        return self

    def build(self) -> Database:
        if self._is_mock:
            return MockDatabase()
        else:
            return MongoDatabase()