from __future__ import annotations

from typing import List

from control_server.src.middleware.headers.byte_convertible import \
    ByteConvertible
from control_server.src.middleware.headers.byte_property import ByteProperty


class MessageHeader(ByteConvertible):
    """
    A header for a message, containing information about the message and its
    size. Useful as it has a fixed size, which makes it easy to read the
    rest of the message without knowing its length prior to receiving.
    """
    def __init__(
            self,
            data: bytes = None,
            copy_from_header: MessageHeader = None,
            extra_properties: List[ByteProperty] = None,
            **kwargs):
        super().__init__(
            endianness='!',
            serialized_properties=[
                ByteProperty(
                    name='message_length',
                    data_format='H'
                ),
                ByteProperty(
                    name='status_code',
                    data_format='B'
                ),
                ByteProperty(
                    name='url_length',
                    data_format='H'
                ),
                ByteProperty(
                    name='body_length',
                    data_format='H'
                ),
                ByteProperty(
                    name='headers_length',
                    data_format='H'
                )
            ] + (extra_properties or [])
        )

        if copy_from_header is None:
            self.message_length: int = -1
            self.status_code: int = -1
            self.url_length: int = -1
            self.body_length: int = -1
            self.headers_length: int = -1

            if data is not None:
                self.load_from_bytes(data)
        else:
            prop_names = self.serialized_properties.keys()
            for prop_name in prop_names:
                setattr(self, prop_name, getattr(copy_from_header, prop_name))

        for (key, value) in kwargs.items():
            setattr(self, key, value)
