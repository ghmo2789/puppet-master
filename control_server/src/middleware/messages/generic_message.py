from __future__ import annotations

import struct

from control_server.src.middleware.checksum import Checksum
from control_server.src.middleware.compression.compression import Compression
from control_server.src.middleware.headers.string_property import StringProperty
from control_server.src.middleware.headers.message_header import MessageHeader


class GenericMessage(MessageHeader):
    _checksum_offset: int = None
    _checksum_size: int = None
    _checksum_type: str = None
    _endianness: str = None

    """
    A generic message that can be sent over the network, containing a URL,
    headers and a body.
    """

    def __init__(
            self,
            message_header: MessageHeader,
            data: bytes = None,
            **kwargs
    ):
        self.url: str = ''
        self.body: str = ''
        self.headers: str = ''

        super().__init__(
            data=data,
            extra_properties=[
                StringProperty(
                    name='url',
                    byte_length=message_header.url_length,
                    getter=lambda: self.url,
                    setter=lambda value: setattr(self, 'url', value)
                ),
                StringProperty(
                    name='body',
                    byte_length=message_header.body_length,
                    getter=lambda: self.body,
                    setter=lambda value: setattr(self, 'body', value)
                ),
                StringProperty(
                    name='headers',
                    byte_length=message_header.headers_length,
                    getter=lambda: self.headers,
                    setter=lambda value: setattr(self, 'headers', value)
                )
            ]
        )

        for prop_name, prop in message_header.serialized_properties.items():
            self.write_prop(
                self.serialized_properties[prop_name],
                message_header.read_prop(prop)
            )

        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def to_bytes(
            self,
            compression: Compression = None,
            checksum: Checksum = None,
            recalculate_checksum: bool = False
    ):
        """
        Converts the message to a byte array, using compression if enabled
        :param recalculate_checksum: Whether to recalculate the checksum
        :param compression: The compression to use. If None, no compression is
        used.
        :return: The byte array representing the message
        """
        all_bytes = super().to_bytes()

        if compression is not None:
            header_bytes = all_bytes[:MessageHeader.size()]
            rest_bytes = all_bytes[MessageHeader.size():]
            all_bytes = header_bytes + compression.compress(rest_bytes)

        if recalculate_checksum:
            all_bytes = GenericMessage.update_data_checksum(
                data=all_bytes,
                checksum=checksum
            )

        return all_bytes

    def calculate_checksum(
            self,
            checksum: Checksum = None,
            compression: Compression = None,
            data: bytes = None
    ):
        """
        Calculates the checksum of the message
        :return: The checksum, as an int
        """
        checksum = checksum or Checksum.read_from_settings()

        data = data or self.to_bytes(compression=compression)

        return GenericMessage.calculate_data_checksum(
            data=data,
            checksum=checksum
        )

    @staticmethod
    def _set_checksum_statics():
        if GenericMessage._checksum_offset is None or \
                GenericMessage._checksum_size is None:
            zero_data = b'\0' * MessageHeader.size()
            instance = GenericMessage(
                message_header=MessageHeader(
                    data=zero_data
                ),
                data=zero_data
            )
            GenericMessage._checksum_offset = instance.offset_of('checksum')
            GenericMessage._checksum_size = instance.size_of('checksum')
            GenericMessage._checksum_type = instance \
                .serialized_properties['checksum'].data_format
            GenericMessage._endianness = instance.endianness

    @staticmethod
    def calculate_data_checksum(
            data: bytes,
            checksum: Checksum = None
    ) -> int:
        GenericMessage._set_checksum_statics()

        checksum = checksum or Checksum.read_from_settings()

        offset = GenericMessage._checksum_offset
        size = GenericMessage._checksum_size

        data = data[:offset] + b'\0' * size + data[offset + size:]

        return checksum.calculate_checksum(data)

    @staticmethod
    def update_data_checksum(
            data: bytes,
            checksum: Checksum = None
    ):
        checksum_value = GenericMessage.calculate_data_checksum(
            data=data,
            checksum=checksum
        )

        checksum_bytes = struct.pack(
            GenericMessage._endianness + GenericMessage._checksum_type,
            checksum_value
        )

        offset = GenericMessage._checksum_offset
        size = GenericMessage._checksum_size

        return data[:offset] + checksum_bytes + data[offset + size:]
