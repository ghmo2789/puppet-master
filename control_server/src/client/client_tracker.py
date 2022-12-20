from datetime import timedelta, datetime
from threading import Timer
from typing import Iterable

from control_server.src.client.client_status_update_event import \
    ClientStatusUpdateEvent
from control_server.src.client.tracked_client import TrackedClient
from control_server.src.utils.event import Event


class ClientTracker:
    def __init__(
            self,
            update_interval: float = 1,
            time_elapsed_factor: float = 2
    ):
        self.active_clients: dict[str, TrackedClient] = {}
        self.inactive_clients: dict[str, TrackedClient] = {}

        self.client_status_changed: Event[ClientStatusUpdateEvent] = Event()
        self.time_elapsed_factor = time_elapsed_factor
        self._tracker_timer = Timer(update_interval, self._do_track_step)
        self._tracker_timer.start()

    def _get_or_create_client(
            self,
            client_id: str,
            polling_time: float
    ) -> TrackedClient:
        if client_id in self.inactive_clients:
            return self.inactive_clients[client_id]

        if client_id not in self.active_clients:
            self.active_clients[client_id] = TrackedClient(
                client_id=client_id,
                polling_time=polling_time
            )

        client = self.active_clients[client_id]
        client.seen()

        return client

    def mark_as_seen(
            self,
            client_id: str,
            polling_time: float,
            is_newly_started: bool):
        client = self._get_or_create_client(
            client_id=client_id,
            polling_time=polling_time
        )

        before_status = client.status
        client.seen(
            is_newly_started=is_newly_started
        )

        if client_id in self.inactive_clients:
            self._move_client(
                client_id=client_id,
                from_dict=self.inactive_clients,
                to_dict=self.active_clients
            )

            after_status = client.status
            self.client_status_changed(
                ClientStatusUpdateEvent(
                    client=client,
                    old_status=before_status,
                    new_status=after_status
                )
            )

        return client

    @staticmethod
    def _move_client(client_id: str, from_dict: dict, to_dict: dict):
        to_dict[client_id] = from_dict.pop(client_id)

    def get_clients(self) -> Iterable[TrackedClient]:
        now = datetime.utcnow()

        for client in self.active_clients.values():
            time_elapsed = now - client.last_seen
            min_time_elapsed = timedelta(
                seconds=client.polling_time * self.time_elapsed_factor
            )

            if time_elapsed < min_time_elapsed:
                continue

            yield client

    def _do_track_step(self):
        elapsed_clients = list(self.get_clients())

        for client in elapsed_clients:
            from_status = client.status
            client.mark_as_inactive()
            to_status = client.status

            self._move_client(
                client_id=client.client_id,
                from_dict=self.active_clients,
                to_dict=self.inactive_clients
            )

            self.client_status_changed(
                ClientStatusUpdateEvent(
                    client=client,
                    old_status=from_status,
                    new_status=to_status
                )
            )
