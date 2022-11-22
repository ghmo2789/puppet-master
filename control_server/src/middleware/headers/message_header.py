import struct


class MessageHeader:
    def __init__(self, data: bytes = None):
        self.message_length: int = -1
        self.status_code: int = -1
        self.url_length: int = -1
        self.body_length: int = -1
        self.headers_length: int = -1

        if data is not None:
            self.load_from_bytes(data)

    def load_from_bytes(self, data: bytes = None):
        if data is None:
            return False

        self.message_length, \
            self.status_code, \
            self.url_length, \
            self.body_length, \
            self.headers_length \
            = struct.unpack('!HBHHH', data)
