from enum import StrEnum


class DatabaseCollection(StrEnum):
    """
    Enum representing the different database collections
    """
    # The collection containing the clients
    USERS = "users"
    # The collection containing the tasks
    USER_TASKS = "user_tasks"
    # The collection containing the completed tasks
    USER_DONE_TASKS = "user_done_tasks"

    # The collection containing the client's responses to tasks
    USER_TASK_RESPONSES = "user_task_responses"

    def get_name(self):
        """
        Gets the name of the collection
        :return: The name of the collection.
        """
        return self.value
