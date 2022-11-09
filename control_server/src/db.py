from decouple import config
from control_server.src.data_class import DataClass
from pymongo import MongoClient

from control_server.src.data.client_data import ClientData


class DatabaseCredentials(DataClass):
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


class Database:
    def __init__(self):
        self.credentials = DatabaseCredentials().read()
        self.client = MongoClient(
            self.credentials.mongo_host,
            port=int(self.credentials.mongo_port),
            username=self.credentials.mongo_user,
            password=self.credentials.mongo_password,
            # authSource=self.credentials.mongo_database,
            authMechanism=self.credentials.mongo_auth_mechanism
        )

        self.db = self.client[self.credentials.mongo_database]
        self.user_collection_name = "clients"

    def set_user(self, id, user: ClientData):
        self.db[self.user_collection_name].insert_one(user.__dict__)
