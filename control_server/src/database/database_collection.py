from enum import StrEnum


class DatabaseCollection(StrEnum):
    """
    Enum representing the different database collections
    """
    # The collection containing the clients
    CLIENTS = "clients"
    # The collection containing the tasks
    CLIENT_TASKS = "client_tasks"
    # The collection containing the completed tasks
    CLIENT_DONE_TASKS = "client_done_tasks"

    # The collection containing the client's responses to tasks
    CLIENT_TASK_RESPONSES = "client_task_responses"

    def get_name(self):
        """
        Gets the name of the collection
        :return: The name of the collection.
        """
        return self.value
