from typing import Generic, List, Callable
from typing import TypeVar

T = TypeVar('T')


class Event(Generic[T]):
    """
    Class representing an event of a specific type, that can have handlers
    """

    def __init__(self):
        self.handlers: List[Callable[[T], None]] = []

    def __iadd__(self, handler: Callable[[T], None]):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler: Callable[[T], None]):
        self.handlers.remove(handler)
        return self

    def __call__(self, data: T):
        for handler in self.handlers:
            handler(data)
