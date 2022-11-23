import struct
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Callable, List, Tuple

from control_server.src.middleware.headers.byte_property import ByteProperty


class ByteConvertible(ABC):
    def __init__(
            self,
            endianness: str = '!',
            serialized_properties: List[ByteProperty] = None):
        self._binary_format: str = endianness
        self._serialized_properties: OrderedDict[str, ByteProperty] = \
            OrderedDict()

        if serialized_properties is not None:
            for prop in serialized_properties:
                self._serialized_properties[prop.name] = prop
                self._binary_format += prop.data_format

    @property
    def binary_format(self) -> str:
        return self._binary_format

    @property
    def serialized_properties(self) -> OrderedDict[str, ByteProperty]:
        return self._serialized_properties

    def load_from_bytes(self, data: bytes = None):
        unpacked_vars = struct.unpack(self.binary_format, data)

        assert len(unpacked_vars) == len(self._serialized_properties)

        for (unpacked_var, prop) in zip(
                unpacked_vars,
                self._serialized_properties.values()
        ):
            self.write_prop(prop, unpacked_var)

    def to_bytes(self) -> bytes:
        pack_vars = [
            self.read_prop(prop) for prop in
            self._serialized_properties.values()
        ]

        return struct.pack(self.binary_format, *pack_vars)

    def write_prop(self, prop: ByteProperty, value: Any):
        if prop.has_writer:
            prop.write(value)
        else:
            setattr(self, prop.name, value)

    def read_prop(self, prop: ByteProperty) -> Any:
        return prop.read() if prop.has_reader else getattr(self, prop.name)
