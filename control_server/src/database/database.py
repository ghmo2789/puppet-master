from __future__ import annotations

from abc import ABC, abstractmethod

from control_server.src.data.client_data import ClientData


class Database(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_user(self, user_id: str, user: ClientData):
        """
        Stores the user with a given ID in the database.
        :param user_id: The user ID to use as a key.
        :param user: The user to store
        :return: Nothing.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: str) -> ClientData:
        """
        Retrieves the user with a given ID from the database.
        :param user_id: The user ID to use as a key.
        :return: The user with the given ID.
        """
        raise NotImplementedError
