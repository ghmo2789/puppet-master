import struct
from abc import ABC
from collections import OrderedDict
from typing import Any, List

from control_server.src.middleware.headers.byte_property import ByteProperty


class ByteConvertible(ABC):
    _type_sizes: dict[str, int] = {}

    """
    A class that can be converted to and from bytes
    """
    def __init__(
            self,
            endianness: str = '!',
            serialized_properties: List[ByteProperty] = None):
        self.endianness: str = endianness
        self._binary_format: str = endianness
        self._serialized_properties: OrderedDict[str, ByteProperty] = \
            OrderedDict()
        self.offsets = {}
        self.sizes = {}

        index = 0
        if serialized_properties is not None:
            for prop in serialized_properties:
                size = ByteConvertible._get_type_size(prop.data_format)

                self.offsets[prop.name] = index
                self.sizes[prop.name] = size

                self._serialized_properties[prop.name] = prop
                self._binary_format += prop.data_format
                index += size

    def offset_of(self, prop_name: str) -> int:
        return self.offsets[prop_name]

    def size_of(self, prop_name: str) -> int:
        return self.sizes[prop_name]

    @staticmethod
    def _get_type_size(data_type: str):
        if data_type in ByteConvertible._type_sizes:
            return ByteConvertible._type_sizes[data_type]

        size = struct.calcsize(data_type)
        ByteConvertible._type_sizes[data_type] = size
        return size

    @property
    def binary_format(self) -> str:
        """
        The binary format string used by Python's struct module
        :return: The binary format string
        """
        return self._binary_format

    @property
    def serialized_properties(self) -> OrderedDict[str, ByteProperty]:
        """
        The properties that are serialized
        :return:
        """
        return self._serialized_properties

    def load_from_bytes(self, data: bytes = None):
        """
        Loads the object from a byte array, by unpacking the data using the
        binary format string and setting the properties accordingly.
        :param data: The byte array to load from
        :return:
        """
        unpacked_vars = struct.unpack_from(self.binary_format, data)

        assert len(unpacked_vars) == len(self._serialized_properties)

        for (unpacked_var, prop) in zip(
                unpacked_vars,
                self._serialized_properties.values()
        ):
            self.write_prop(prop, unpacked_var)

    def to_bytes(self) -> bytes:
        """
        Converts the object to a byte array, by packing the properties using the
        binary format string.
        :return: The byte array representation of the object
        """
        pack_vars = [
            self.read_prop(prop) for prop in
            self._serialized_properties.values()
        ]

        return struct.pack(self.binary_format, *pack_vars)

    def write_prop(self, prop: ByteProperty, value: Any):
        """
        Writes a value to a property of the object
        :param prop: The property to write to
        :param value: The value to write
        :return:
        """
        if prop.has_writer:
            prop.write(value)
        else:
            setattr(self, prop.name, value)

    def read_prop(self, prop: ByteProperty) -> Any:
        """
        Reads a value from a property of the object
        :param prop: The property to read from
        :return: The value read
        """
        return prop.read() if prop.has_reader else getattr(self, prop.name)
