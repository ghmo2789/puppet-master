import uuid
from typing import cast, Iterable

from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.task_status import TaskStatus
from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.client_task import ClientTask
from control_server.src.data.task import Task


def generate_random_id() -> str:
    return str(uuid.uuid4())


def randomize_ids() -> (str, str):
    """
    TODO: Add comment here
    """
    client_id = generate_random_id()
    client_ip = generate_random_id()
    return client_id, client_ip


def set_client(client_id: str, client_ip: str):
    """
    Helper function for setting a client in the database
    """
    client_1 = {
        "os_name": "2",
        "os_version": "2",
        "hostname": "2",
        "host_user": "2",
        "privileges": "2",
    }
    client_data = ClientData.load_from_dict(client_1, raise_error=True)
    new_client = IdentifyingClientData(
        client_data=client_data,
        ip=client_ip
    )
    new_client.set_id(client_id)
    controller.db.set_client(
        client_id=client_id,
        client=new_client,
        overwrite=True
    )


def test_post_invalid_authorization(client):
    """
    Test the /admin/task post endpoint with missing authorization
    :param client:
    :return:
    """
    response = client.post(
        f"{get_prefix()}/admin/task", json={

        }
    )
    assert response.status_code == 401, \
        "Received a non-401 status code"


def test_post_task_wrong_client_id(client):
    """
    Test the /admin/task post endpoint with wrong client id
    :param client:
    :return:
    """
    response_missing_client_id = client.post(
        f"{get_prefix()}/admin/task", headers={
            "Authorization": controller.settings.admin_key
        }, json={

        }
    )

    response_wrong_client_id = client.post(
        f"{get_prefix()}/admin/task", headers={
            "Authorization": controller.settings.admin_key
        }, json={
            "client_id": "1234",
            "data": "test",
            "name": "test",
            "min_delay": "0",
            "max_delay": "0"
        }
    )
    assert response_missing_client_id.status_code == 400, \
        "Received a non-400 status code"
    assert response_wrong_client_id == 404, \
        "Received a non-404 status code"


def test_post_task_missing_task(client):
    """
    Test the /admin/task post endpoint with missing task
    :param client:
    :return:
    """
    response_missing_task = client.post(
        f"{get_prefix()}/admin/task", headers={
            "Authorization": controller.settings.admin_key
        }, json={
            "client_id": "1234"
        }
    )
    assert response_missing_task.status_code == 400, \
        "Received a non-404 status code"


def test_post_task(client):
    """
    Test the /admin/task post endpoint
    :param client:
    :return:
    """
    # Set client in DB
    client_id, client_ip = randomize_ids()
    set_client(client_id=client_id, client_ip=client_ip)

    response = client.post(
        f"{get_prefix()}/admin/task", headers={
            "Authorization": controller.settings.admin_key
        }, json={
            "client_id": client_id,
            "data": "test",
            "name": "test",
            "min_delay": "0",
            "max_delay": "0"
        }
    )

    task_id = response.get_data(as_text=True)
    client_task = cast(
        ClientTask,
        controller.db.get_one(
            collection=DatabaseCollection.CLIENT_TASKS,
            identifier={
                "_id.task_id": task_id
            },
            entry_instance=ClientTask()
        )
    )
    assert response.status_code == 200, \
        "Received a non-200 status code"
    assert client_task.id.get("task_id") == task_id
    assert client_task.id.get("client_id") == client_id
    assert client_task.status_code == -2
    assert client_task.status == TaskStatus.PENDING


def test_post_task_abort_task(client):
    """
    Test the /admin/task post endpoint, by posting a task, and then an abort
    task aborting the newly posted task.
    :param client:
    :return:
    """
    # Set client in DB
    client_id, client_ip = randomize_ids()
    set_client(client_id=client_id, client_ip=client_ip)

    # Post the task
    posted_task_id = _post_task(
        client=client,
        client_id=client_id
    )

    search_criteria = {
        "_id.client_id": client_id
    }

    _assert_tasks(
        search_criteria=search_criteria,
        collection=DatabaseCollection.CLIENT_TASKS,
        ids=[posted_task_id],
        statuses=[TaskStatus.PENDING]
    )

    # Post the abort task
    abort_task_id = _post_task(
        client=client,
        client_id=client_id,
        task_name="abort",
        task_data=posted_task_id
    )

    # CLIENT_TASKS should not contain any tasks for the client since the control
    # server should have aborted the task, and moved both the abort task and
    # the task to the CLIENT_DONE_TASKS collection
    _assert_tasks(
        search_criteria=search_criteria,
        collection=DatabaseCollection.CLIENT_TASKS,
        ids=[],
        statuses=[]
    )

    # Both tasks should be in the CLIENT_DONE_TASKS collection, with their
    # statuses being either ABORTED (for the task) or DONE (for the
    # aborting task)
    _assert_tasks(
        search_criteria=search_criteria,
        collection=DatabaseCollection.CLIENT_DONE_TASKS,
        ids=[posted_task_id, abort_task_id],
        statuses=[TaskStatus.ABORTED, TaskStatus.DONE]
    )


def test_post_task_abort_non_existing_task(client):
    """
    Test the /admin/task post endpoint, by posting an abort task for a task
    that is not in the pending tasks collection.
    :param client:
    :return:
    """
    # Set client in DB
    client_id, client_ip = randomize_ids()
    set_client(client_id=client_id, client_ip=client_ip)

    # Post the task
    search_criteria = {
        "_id.client_id": client_id
    }

    _assert_tasks(
        search_criteria=search_criteria,
        collection=DatabaseCollection.CLIENT_TASKS,
        ids=[],
        statuses=[]
    )

    # Post the abort task
    abort_task_id = _post_task(
        client=client,
        client_id=client_id,
        task_name="abort",
        task_data=generate_random_id()
    )

    _assert_tasks(
        search_criteria=search_criteria,
        collection=DatabaseCollection.CLIENT_TASKS,
        ids=[abort_task_id],
        statuses=[TaskStatus.PENDING]
    )


def _assert_tasks(
        search_criteria: dict,
        collection: DatabaseCollection,
        ids: list[str] = None,
        statuses: list[TaskStatus] = None
) -> Iterable[ClientTask]:
    """
    Asserts that the tasks in the specified collection matches the IDs and
    statuses specified in the arguments, and that the number of tasks match the
    number of IDs and statuses specified.
    :param search_criteria: The search criteria to use when searching the
    collection.
    :param collection: The collection to search.
    :param ids: The IDs to assert.
    :param statuses: The statuses to assert.
    :return: The tasks that were found in the collection.
    """
    if ids is None:
        allowed_statuses = []

    if statuses is None:
        allowed_ids = []

    tasks = cast(
        list[ClientTask],
        controller.db.get_all(
            collection=collection,
            entry_instance=ClientTask(),
            identifier=search_criteria
        )
    )

    assert len(tasks) == len(ids) == len(statuses), \
        f"Number of tasks ({len(tasks)}) does not match number of expected " \
        f"ids ({len(ids)}) and number of statuses ({len(statuses)})"

    for task, expected_id, expected_status in zip(tasks, ids, statuses):
        assert task.get_task_id() == expected_id, \
            f"Expected task id {expected_id}, got {task.get_task_id()}"
        assert task.status == expected_status, \
            f"Expected task status {expected_status}, got {task.status}"

        yield task


def _post_task(
        client,
        client_id: str,
        task_name: str = "test",
        task_data: str = "test"
):
    response = client.post(
        f"{get_prefix()}/admin/task", headers={
            "Authorization": controller.settings.admin_key
        }, json={
            "client_id": client_id,
            "data": task_data,
            "name": task_name,
            "min_delay": "0",
            "max_delay": "0"
        }
    )

    assert response.status_code == 200, \
        "Received a non-200 status code"

    return response.get_data(as_text=True)
