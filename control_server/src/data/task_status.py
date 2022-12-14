from enum import StrEnum


class TaskStatus(StrEnum):
    """
    Enum representing the different statuses of client tasks
    """
    DONE = "done"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    ABORTED = "aborted"

    def get_name(self):
        """
        Gets the name of the status
        :return: The name of the status.
        """
        return self.value

    def get_code(self):
        """
        Gets the code of the status
        :return: The code of the status.
        """
        codes = {
            TaskStatus.DONE: 0,
            TaskStatus.ERROR: 1,
            TaskStatus.IN_PROGRESS: -1,
            TaskStatus.PENDING: -2,
            TaskStatus.ABORTED: -3
        }

        return codes[self]
