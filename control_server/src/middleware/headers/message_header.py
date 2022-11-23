from control_server.src.middleware.headers.byte_convertible import \
    ByteConvertible
from control_server.src.middleware.headers.byte_property import ByteProperty


class MessageHeader(ByteConvertible):
    def __init__(self, data: bytes = None):
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
            ]
        )

        self.message_length: int = -1
        self.status_code: int = -1
        self.url_length: int = -1
        self.body_length: int = -1
        self.headers_length: int = -1

        if data is not None:
            self.load_from_bytes(data)

    # def load_from_bytes(self, data: bytes = None):
    #     if data is None:
    #         return False
    #
    #     self.message_length, \
    #     self.status_code, \
    #     self.url_length, \
    #     self.body_length, \
    #     self.headers_length \
    #         = struct.unpack('!HBHHH', data)
    #
    # def to_bytes(self) -> bytes:
    #     return struct.pack(
    #         '!HBHHH',
    #         self.message_length,
    #         self.status_code,
    #         self.url_length,
    #         self.body_length,
    #         self.headers_length)
