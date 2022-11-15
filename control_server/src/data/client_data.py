from control_server.src.data_class import DataClass


class ClientData(DataClass):
    def __init__(self):
        super().__init__()
        self.os_name = None
        self.os_version = None
        self.hostname = None
        self.host_user = None
        self.privileges = None
