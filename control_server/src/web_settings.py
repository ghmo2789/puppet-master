from decouple import config

from control_server.src.data_class import DataClass


class WebSettings(DataClass):
    def __init__(self):
        super().__init__()
        self._prefix = None

    def read(self):
        self.load_from(lambda prop:
                       config(prop.lstrip("_").upper()))
        return self

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = value