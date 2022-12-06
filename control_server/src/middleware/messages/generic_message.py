from control_server.src.middleware.headers.string_property import StringProperty
from control_server.src.middleware.headers.message_header import MessageHeader


class GenericMessage(MessageHeader):
    """
    A generic message that can be sent over the network, containing a URL,
    headers and a body.
    """

    def __init__(
            self,
            message_header: MessageHeader,
            data: bytes = None,
            **kwargs):
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
