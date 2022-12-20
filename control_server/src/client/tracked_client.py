from datetime import datetime

from control_server.src.client.client_status import ClientStatus


class TrackedClient:
    def __init__(
            self,
            client_id: str,
            polling_time: float,
            default_status: ClientStatus = ClientStatus.ACTIVE
    ):
        self.client_id: str = client_id
        self.last_seen: datetime = datetime.utcnow()
        self.status = default_status
        self.polling_time = polling_time

    def seen(self, is_newly_started: bool = False):
        self.last_seen = datetime.utcnow()
        self.status = ClientStatus.STARTED \
            if is_newly_started else \
            ClientStatus.ACTIVE

    def mark_as_inactive(self):
        self.status = ClientStatus.INACTIVE
