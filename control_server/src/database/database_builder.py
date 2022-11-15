from control_server.src.database.database import Database
from control_server.src.database.mock_database import MockDatabase
from control_server.src.database.mongo_database import MongoDatabase


class DatabaseBuilder:
    """
    Builder class for building an instance of the database class
    """
    def __init__(self):
        self._is_mock = False

    def set_mock(self, is_mock: bool):
        """
        Set whether the database should be a mock database.
        :param is_mock: Whether the database should be a mock database
        :return: The builder instance
        """
        self._is_mock = is_mock
        return self

    def build(self) -> Database:
        """
        Build the database instance
        :return: The built database instance
        """
        if self._is_mock:
            return MockDatabase()
        else:
            return MongoDatabase()
