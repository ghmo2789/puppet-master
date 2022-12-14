from abc import ABC


class IpMessage(ABC):
    """
    An IP message, containing a sender address
    """
    def __init__(self, address: str):
        self._address: str = address

    @property
    def address(self) -> str:
        return self._address
