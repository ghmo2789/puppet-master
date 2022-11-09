from control_server.src.data_class import DataClass


class ClientData(DataClass):
    def __init__(self):
        super().__init__()
        self.os_name = None
        self.os_version = None
        self.computer_name = None
        self.computer_user = None
        self.privileges = None