from typing import cast

from control_server.src.client.client_status import ClientStatus
from control_server.src.data.client_task import ClientTask
from control_server.src.data.task_status import TaskStatus
from control_server.src.database.database import Database
from control_server.src.database.database_collection import DatabaseCollection


class ClientTaskStatusUpdater:
    def __init__(self, db: Database):
        self.db: Database = db

    def update_status(self, client_id: str, status: ClientStatus):
        """
        Update the status of all tasks assigned to the client with the given
        client ID depending on the client's status. If the client goes inactive,
        all tasks assigned to the client are marked as unknown. If the client
        goes back online with a new init, all tasks assigned to the client
        are marked as aborted.
        :param client_id: The ID of the client
        :param status: The status of the client
        :return:
        """
        if status == ClientStatus.INACTIVE:
            # Client just became inactive. It is unknown whether the tasks
            # assigned to the client are still running or not. Mark all tasks
            # as unknown.
            self._set_in_progress_task_status(
                client_id=client_id,
                from_collection=DatabaseCollection.CLIENT_TASKS,
                to_collection=DatabaseCollection.CLIENT_TASKS,
                task_status=TaskStatus.IN_PROGRESS,
                new_task_status=TaskStatus.UNKNOWN
            )
        elif status == ClientStatus.ACTIVE:
            # Client goes from inactive/starting to active. Because going from
            # inactive to starting moves tasks to CLIENT_DONE_TASKS collection,
            # all UNKNOWN tasks in CLIENT_TASKS can be changed to IN_PROGRESS,
            # because the client probably have lost connection to the server
            # and later regained it, without having restarted.
            self._set_in_progress_task_status(
                client_id=client_id,
                from_collection=DatabaseCollection.CLIENT_TASKS,
                to_collection=DatabaseCollection.CLIENT_TASKS,
                task_status=TaskStatus.UNKNOWN,
                new_task_status=TaskStatus.IN_PROGRESS
            )
        elif status == ClientStatus.STARTED:
            # Client just started. Therefore, it is known that the client is not
            # running any tasks. Therefore, set all tasks with unknown status
            # to ABORTED.
            self._set_in_progress_task_status(
                client_id=client_id,
                from_collection=DatabaseCollection.CLIENT_TASKS,
                to_collection=DatabaseCollection.CLIENT_DONE_TASKS,
                task_status=TaskStatus.UNKNOWN,
                new_task_status=TaskStatus.ABORTED
            )

    def _get_tasks_with_status(
            self,
            client_id: str,
            collection: DatabaseCollection,
            task_status: TaskStatus
    ) -> list[ClientTask]:
        return cast(
            list[ClientTask],
            self.db.get_all(
                collection=collection,
                identifier={
                    '_id.client_id': client_id,
                    'status': task_status.get_name()
                },
                entry_instance_creator=lambda: ClientTask()
            )
        )

    def _set_in_progress_task_status(
            self,
            client_id: str,
            from_collection: DatabaseCollection,
            to_collection: DatabaseCollection,
            task_status: TaskStatus,
            new_task_status: TaskStatus
    ) -> int:
        """
        Set the status of all tasks assigned to the client that have a
        specific status to another specified status
        :return:
        """
        client_tasks = self._get_tasks_with_status(
            client_id=client_id,
            collection=from_collection,
            task_status=task_status
        )

        for client_task in client_tasks:
            client_task.set_status(new_task_status)
            key = {
                '_id.client_id': client_id,
                '_id.task_id': client_task.get_task_id()
            }

            self.db.set(
                collection=to_collection,
                identifier=key,
                entry=client_task
            )

            # If the task should be moved, remove it from the collection it is
            # moved from.
            if from_collection != to_collection:
                self.db.delete(
                    collection=from_collection,
                    identifier=key
                )

        return len(client_tasks)
