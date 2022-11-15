from control_server.src.data_class import DataClass


class ClientIdentifier(DataClass):
    def __init__(self):
        super().__init__()
        self.authorization = None
