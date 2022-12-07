from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage


class GenericMessageBuilder:
    def __init__(self):
        self.url: str = ''
        self.body: str = ''
        self.headers: str = ''
        self.url_length: int = -1
        self.body_length: int = -1
        self.headers_length: int = -1
        self.status_code: int = -1

    def set_url(self, url: str):
        self.url = url
        self.url_length = len(url.encode('utf-8'))
        return self

    def set_body(self, body: str):
        self.body = body
        self.body_length = len(body.encode('utf-8'))
        return self

    def set_headers(self, headers: str):
        self.headers = headers
        self.headers_length = len(headers.encode('utf-8'))
        return self

    def set_url_length(self, url_length: int):
        self.url_length = url_length
        return self

    def set_body_length(self, body_length: int):
        self.body_length = body_length
        return self

    def set_headers_length(self, headers_length: int):
        self.headers_length = headers_length
        return self

    def set_status_code(self, status_code: int):
        self.status_code = status_code
        return self

    def build(self):
        header = MessageHeader(
            message_length=MessageHeader.size() +
                self.url_length +
                self.body_length +
                self.headers_length,
            url_length=self.url_length,
            body_length=self.body_length,
            headers_length=self.headers_length,
            status_code=self.status_code
        )

        return GenericMessage(
            message_header=header,
            url=self.url,
            body=self.body,
            headers=self.headers
        )
