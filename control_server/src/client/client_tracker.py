from datetime import timedelta, datetime
from threading import Timer, Thread, Lock
from typing import Iterable

from control_server.src.client.client_status import ClientStatus
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
        self._update_mutex = Lock()

    def force_update(self):
        if not self.update(timeout=-1):
            raise RuntimeError("Could not force update. Update failed.")

    def update(self, timeout: float = None) -> bool:
        return self._do_track_step(timeout=timeout)

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

    def get_status(self, client_id: str) -> ClientStatus | None:
        """
        Retrieves the status of a specified client if it is being tracked,
        otherwise None.
        :param client_id: The ID of the client to retrieve a status for
        :return: The status of the client
        """
        if client_id in self.active_clients:
            return self.active_clients[client_id].status

        if client_id in self.inactive_clients:
            return self.inactive_clients[client_id].status

        return None

    def mark_as_seen(
            self,
            client_id: str,
            polling_time: float,
            is_newly_started: bool
    ):
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

    def _do_track_step(self, timeout: float = None) -> bool:
        """
        Performs a single tracking step, i.e. checks if any clients have been
        inactive for too long and marks them as inactive if so.
        :param timeout: The timeout for acquiring the mutex. If None, the
        no timeout is used, and the function returns False immediately if the
        mutex cannot be acquired immediately. If a timeout is specified, the
        function will wait for the specified amount of time for the mutex to
        become available, and return True if the mutex was acquired, and False
        if the timeout was reached.
        :return: True if the tracking step was successfully performed, i.e. the
        mutex was taken and no errors occurred. False otherwise.
        """
        lock_status = self._update_mutex.acquire(timeout=timeout) \
            if timeout is not None else \
            self._update_mutex.acquire(blocking=False)

        if not lock_status:
            return False

        try:
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

            return True
        finally:
            self._update_mutex.release()
