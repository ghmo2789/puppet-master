from typing import Callable

from control_server.src.middleware.headers.byte_property import ByteProperty


class StringProperty(ByteProperty):
    def __init__(
            self,
            name: str,
            byte_length: int,
            encoding: str = 'utf-8',
            getter: Callable[[], str] = None,
            setter: Callable[[str], None] = None):
        self._getter = getter
        self._setter = setter

        super().__init__(
            name=name,
            data_format=f'{byte_length}s',
            reader=lambda: self._getter().encode(encoding),
            writer=lambda value: self._setter(value.decode(encoding))
        )
