from control_server.src.client.client_status import ClientStatus
from control_server.src.client.tracked_client import TrackedClient


class ClientStatusUpdateEvent:
    def __init__(
            self,
            client: TrackedClient,
            old_status: ClientStatus,
            new_status: ClientStatus
    ):
        self.client: TrackedClient = client
        self.old_status: ClientStatus = old_status
        self.new_status: ClientStatus = new_status

