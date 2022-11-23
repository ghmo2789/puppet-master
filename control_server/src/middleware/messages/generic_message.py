from control_server.src.middleware.headers.StringProperty import StringProperty
from control_server.src.middleware.headers.byte_property import ByteProperty
from control_server.src.middleware.headers.message_header import MessageHeader


class GenericMessage(MessageHeader):
    def __init__(
            self,
            message_header: MessageHeader,
            data: bytes = None):
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

        self.url: str = ''
        self.body: str = ''
        self.headers: str = ''
