from abc import ABC
from typing import Any


class IpMessage(ABC):
    """
    An IP message, containing a sender address
    """
    def __init__(self, address: str):
        self._address: str = address

    @property
    def address(self) -> str:
        return self._address
