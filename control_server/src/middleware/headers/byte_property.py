from typing import Callable, Any, TypeVar, Generic

T = TypeVar('T')


class ByteProperty(Generic[T]):
    """
    A property that can be serialized to and from bytes
    """
    def __init__(
            self,
            name: str,
            data_format: str,
            reader: Callable[[], T] = None,
            writer: Callable[[T], None] = None):
        self.name = name
        self.data_format = data_format
        self.reader = reader
        self.writer = writer
        self.has_writer = writer is not None
        self.has_reader = reader is not None

    def read(self) -> T:
        """
        Reads the value of the property
        :return: The value of the property
        """
        return self.reader()

    def write(self, value: T):
        """
        Writes a value to the property
        :param value: The value to write
        :return:
        """
        self.writer(value)
