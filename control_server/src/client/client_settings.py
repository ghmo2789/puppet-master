from decouple import config

from control_server.src.data_class import DataClass


class ClientSettings(DataClass):
    def __init__(self):
        super().__init__()
        self._update_interval = 1
        self._time_elapsed_factor = 2

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
    def update_interval(self) -> float:
        return self._update_interval

    @property
    def time_elapsed_factor(self) -> float:
        return self._time_elapsed_factor

