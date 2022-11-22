class HashableDict(dict):
    """
    Hashable wrapper for the dict class, allowing it to be used as a key in a
    dictionary.
    """
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def __eq__(self, other):
        return dict(self) == dict(other)
