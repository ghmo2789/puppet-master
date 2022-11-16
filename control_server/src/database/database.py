from __future__ import annotations

from abc import ABC, abstractmethod

from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData


class Database(ABC):
    """
    An abstract database class, useful for abstracting how the database is
    implemented, and how the data is stored.
    """
    def __init__(self):
        pass

    @abstractmethod
    def set_user(
            self,
            user_id: str,
            user: IdentifyingClientData,
            overwrite: bool = False):
        """
        Stores the user with a given ID in the database.
        :param user_id: The user ID to use as a key.
        :param user: The user to store
        :param overwrite: Whether to overwrite the user if it already exists
        :return: Nothing.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """
        Deletes the user with a given ID from the database.
        :param user_id: The user ID of the user to delete
        :return: Whether the user was deleted from the database.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: str) -> IdentifyingClientData:
        """
        Retrieves the user with a given ID from the database.
        :param user_id: The user ID to use as a key.
        :return: The user with the given ID.
        """
        raise NotImplementedError

    def clear(self):
        """
        Clears the database.
        :return: Nothing.
        """
        raise NotImplementedError
