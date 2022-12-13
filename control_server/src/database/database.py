from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Any

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.serializable import Serializable
from control_server.src.database.database_collection import DatabaseCollection


class Database(ABC):
    """
    An abstract database class, useful for abstracting how the database is
    implemented, and how the data is stored.
    """

    def __init__(self):
        pass

    @staticmethod
    def _verify_identifier_entry_id(
            entry_id: str,
            identifier: dict[str, Any]
    ):
        if entry_id is not None and identifier is not None:
            raise ValueError("Cannot specify both entry_id and identifier")

        if entry_id is None and identifier is None:
            raise ValueError("Must specify either entry_id or identifier")

    @abstractmethod
    def set(
            self,
            collection: DatabaseCollection,
            entry: Serializable,
            entry_id: str = None,
            identifier: dict[str, Any] = None,
            overwrite: bool = False,
            ignore_id: bool = False
    ):
        """
        Stores an entry with a given ID in the database.
        :param ignore_id: Whether to ignore the _id of the entry when storing.
        :param collection: The database collection to store to.
        :param entry_id: The ID of the entry to store.
        :param identifier: The identifier of the entry to store.
        :param entry: The entry to store
        :param overwrite: Whether to overwrite the client if it already exists
        :return: Nothing.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
            self,
            collection: DatabaseCollection,
            entry_id: str = None,
            identifier: dict[str, Any] = None
    ) -> bool:
        """
        Deletes the entry with the given ID from the specified database
        collection.
        :param collection: Collection to delete from
        :param entry_id: The entry ID of the entry to delete
        :param identifier: The identifier of the entry to delete
        :return: Whether the entry was deleted from the database.
        """
        raise NotImplementedError

    @abstractmethod
    def get_one(
            self,
            collection: DatabaseCollection,
            entry_id: str = None,
            identifier: dict[str, Any] = None,
            entry_instance: Deserializable = None
    ) -> Deserializable | None:
        """
        Retrieves an entry with a given ID from a specified database collection.
        :param collection: The collection of the database to get an entry from.
        :param entry_id: The entry ID to use as a key.
        :param identifier: A dictionary of key-value pairs to use as a key.
        :param entry_instance: An instance of the entry to load data into.
        :return: The entry instance, if data was retrieved from the database.
        None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(
            self,
            collection: DatabaseCollection,
            identifier: Dict[str, Any],
            entry_instance_creator: Callable[[], Deserializable]
    ) -> List[Deserializable]:
        """
        Retrieves all entries with a given identifier from a specified
        database collection.
        :param collection: The collection of the database to get an entry from.
        :param identifier: The identifier to search for.
        :param entry_instance_creator: A function to create instances of the
        type of entry to retrieve
        :return: The entries retrieved from the database.
        """
        raise NotImplementedError

    @abstractmethod
    def set_client(
            self,
            client_id: str,
            client: IdentifyingClientData,
            overwrite: bool = False
    ):
        """
        Stores the client with a given ID in the database.
        :param client_id: The client ID to use as a key.
        :param client: The client to store
        :param overwrite: Whether to overwrite the client if it already exists
        :return: Nothing.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_client(self, client_id: str) -> bool:
        """
        Deletes the client with a given ID from the database.
        :param client_id: The client ID of the client to delete
        :return: Whether the client was deleted from the database.
        """
        raise NotImplementedError

    @abstractmethod
    def get_client(self, client_id: str) -> IdentifyingClientData:
        """
        Retrieves the client with a given ID from the database.
        :param client_id: The client ID to use as a key.
        :return: The client with the given ID.
        """
        raise NotImplementedError

    def clear(self):
        """
        Clears the database.
        :return: Nothing.
        """
        raise NotImplementedError
