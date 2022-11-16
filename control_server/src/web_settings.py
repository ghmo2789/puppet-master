from decouple import config

from control_server.src.data_class import DataClass


class WebSettings(DataClass):
    def __init__(self):
        super().__init__()
        self._prefix = ''
        self._mock_db = False
        self._debug = False
        self._behind_proxy = True
        self._id_key = ''

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
    def behind_proxy(self) -> bool:
        return self._behind_proxy

    @property
    def id_key(self) -> str:
        return self._id_key

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
