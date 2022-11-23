from typing import List, Set

from decouple import config

from control_server.src.data_class import DataClass


class WebSettings(DataClass):
    def __init__(self):
        super().__init__()
        self._prefix = ''
        self._mock_db = False
        self._debug = False
        self._trusted_proxies: str = ''
        self._id_key = ''
        self._admin_key = ''

    def read(self):
        self.load_from_with_types(
            lambda prop, prop_type:
            config(
                prop.lstrip("_").upper(),
                cast=prop_type
            )
        )

        return self

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def trusted_proxies(self) -> str:
        return self._trusted_proxies

    @property
    def trusted_proxies_set(self) -> Set[str]:
        return set(self._trusted_proxies.split(','))

    @property
    def id_key(self) -> str:
        return self._id_key

    @property
    def admin_key(self) -> str:
        return self._admin_key

    @prefix.setter
    def prefix(self, value: str):
        self._prefix = value

    @property
    def mock_db(self) -> bool:
        return self._mock_db

    @property
    def debug(self) -> bool:
        return self._debug

    @mock_db.setter
    def mock_db(self, value: bool):
        self._mock_db = value
