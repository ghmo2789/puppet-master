from control_server.src.data_class import DataClass


class ClientIdentifier(DataClass):
    """
    A data class containing the identification information for a client.
    """
    def __init__(self):
        super().__init__()
        self.authorization = None
