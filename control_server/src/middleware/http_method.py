from __future__ import annotations
from enum import Enum


class HttpMethod(Enum):
    """
    Enum representing an HTTP method
    """
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
    def from_int(value: int, raise_error: bool = True) -> HttpMethod | int:
        """
        Gets the HttpMethod from an integer.
        :param raise_error: Whether to raise an error if the value is
        not found
        :param value: The integer value.
        :return: The HttpMethod.
        """
        for method in HttpMethod:
            if method.get_value() == value:
                return method

        if raise_error:
            raise ValueError('Invalid HttpMethod value.')

        return value

    @staticmethod
    def to_string(method: HttpMethod | int):
        if isinstance(method, int):
            return str(method)

        return method.name

    def get_value(self):
        """
        Gets the name of the collection
        :return: The name of the collection.
        """
        return self.value[0]
