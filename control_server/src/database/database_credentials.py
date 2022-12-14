from __future__ import annotations

from decouple import config

from control_server.src.data_class import DataClass


class DatabaseCredentials(DataClass):
    """
    Data class containing the credentials for the database
    """
    def __init__(self):
        super().__init__()
        self.mongo_host = None
        self.mongo_port = None
        self.mongo_user = None
        self.mongo_password = None
        self.mongo_database = None
        self.mongo_auth_mechanism = None

    def read(self):
        self.load_from(lambda prop: config(prop.upper()))
        return self
