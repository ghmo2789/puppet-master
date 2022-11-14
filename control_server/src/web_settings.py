from decouple import config

from control_server.src.data_class import DataClass


class WebSettings(DataClass):
    def __init__(self):
        super().__init__()
        self._prefix = None
        self._mock_db = None

    def read(self):
        self.load_from(lambda prop:
                       config(prop.lstrip("_").upper()))
        return self

    @property
    def prefix(self) -> str:
        return self._prefix

    @prefix.setter
    def prefix(self, value: str):
        self._prefix = value

    @property
    def mock_db(self) -> bool:
        return self._mock_db

    @prefix.setter
    def set_mock_db(self, value: bool):
        self._mock_db = value
