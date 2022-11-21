class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def __eq__(self, other):
        return dict(self) == dict(other)
