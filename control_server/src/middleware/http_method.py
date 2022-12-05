from enum import Enum


class HttpMethod(Enum):
    GET = 1,
    HEAD = 2,
    POST = 3,
    PUT = 4,
    DELETE = 5,
    CONNECT = 6,
    OPTIONS = 7,
    TRACE = 8,
    PATCH = 9

    @staticmethod
    def from_int(value: int):
        """
        Gets the HttpMethod from an integer.
        :param value: The integer value.
        :return: The HttpMethod.
        """
        for method in HttpMethod:
            if method.get_value() == value:
                return method

        raise ValueError('Invalid HttpMethod value.')

    def get_value(self):
        """
        Gets the name of the collection
        :return: The name of the collection.
        """
        return self.value[0]
