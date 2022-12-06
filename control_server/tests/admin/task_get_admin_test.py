import uuid

from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.data.task import Task
from control_server.src.data.client_task import ClientTask
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.task_status import TaskStatus
from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import IdentifyingClientData
from control_server.src import router


def randomize_ids() -> (str, str):
    """
    Randomizes the client and task IDs. Useful to prevent key collisions in
    database during testing. UUIDs are 128-bits, so the chance of collision by
    generating the same IDs twice is negligible.
    :return:
    """
    client_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    return client_id, task_id


def set_client_and_task(client_id: str, task_id: str, db_collection: DatabaseCollection,
                        task_status: TaskStatus):
    """
    Helper function for setting a client and task in the database
    """
    client_ip = str(uuid.uuid4())
    task = Task(
        name="0",
        data="0",
        min_delay=0,
        max_delay=0
    ).with_id()
    client_task = ClientTask(
        client_id=client_id,
        task_id=task_id,
        task=task,
    )
    client_task.set_status(status=task_status)
    client_task.set_status_code(status_code=0)

    # Set user in DB
    client_1 = {
        "os_name": "2",
        "os_version": "2",
        "hostname": "2",
        "host_user": "2",
        "privileges": "2",
    }
    data = ClientData.load_from_dict(client_1, raise_error=True)
    new_client = IdentifyingClientData(
        client_data=data,
        ip=client_ip
    )
    new_client.set_id(client_id)
    controller.db.set_user(
        user_id=client_id,
        user=new_client,
        overwrite=True
    )

    controller.db.set(
        collection=db_collection,
        entry_id=client_task.id,
        entry=client_task,
        overwrite=True
    )


def test_get_task_invalid_authorization(client):
    """
    Test the /admin/task get endpoint with missing authorization
    :param client:
    :return:
    """
    response = client.get(f"{get_prefix()}/admin/task", headers={

    })

    assert response.status_code == 401, "Received a non-401 status code"


def test_get_task_wrong_client_id(client):
    """
    Test the /admin/task get endpoint with wrong client id
    :param client:
    :return:
    """
    wrong_client_id = "1234"
    response = client.get(f"{get_prefix()}/admin/task", headers={
        "Authorization": controller.settings.admin_key
    }, query_string={
        "id": wrong_client_id
    })

    assert response.status_code == 404, "Received a non-404 status code"


def test_get_task_wrong_task_id(client):
    """
    Test the /admin/task get endpoint with wrong task id
    :param client:
    :return:
    """
    wrong_client_id = "1234"
    wrong_task_id = "1234"
    response = client.get(f"{get_prefix()}/admin/task",
                          headers={
                              "Authorization": controller.settings.admin_key
                          },
                          query_string={
                              "id": wrong_client_id,
                              "task_id": wrong_task_id
                          })

    assert response.status_code == 404, "Received a non-404 status code"


def test_get_task_pending_tasks(client):
    """
    Test the /admin/task get endpoint with pending task
    :param client:
    :return:
    """
    client_id, task_id = randomize_ids()

    no_task_response = client.get(f"{get_prefix()}/admin/task",
                                  headers={
                                      "Authorization": controller.settings.admin_key
                                  },
                                  query_string={
                                      "id": client_id,
                                      "task_id": task_id
                                  })

    assert no_task_response.status_code == 404, "Received a non-404 status code"

    # Insert a user and task in the DB
    set_client_and_task(client_id=client_id,
                        task_id=task_id,
                        db_collection=DatabaseCollection.USER_TASKS,
                        task_status=TaskStatus.PENDING)

    response = \
        client.get(f"{get_prefix()}/admin/task",
                   headers={
                       "Authorization": controller.settings.admin_key
                   },
                   query_string={
                       "id": client_id,
                       "task_id": task_id
                   })

    pending_tasks = response.json.get("pending_tasks")
    sent_tasks = response.json.get("sent_tasks")

    pending_client_task = ClientTask().deserialize(pending_tasks[0])

    assert len(sent_tasks) == 1, "Incorrect number of sent tasks"
    assert len(pending_tasks) == 1, "Incorrect number of pending tasks"
    assert pending_client_task.id.get('client_id') == client_id, "Client ID does not match"
    assert pending_client_task.get_task_id() == task_id, "Task ID does not match"
    assert pending_client_task.status == TaskStatus.DONE, "Task status does not match"
    assert pending_client_task.status_code == 0, "Status code does not match"


def test_get_task_sent_tasks(client):
    """
    Test the /admin/task get endpoint with sent task
    :param client:
    :return:
    """
    client_id, task_id = randomize_ids()

    # Insert a user and task in the DB
    set_client_and_task(client_id=client_id,
                        task_id=task_id,
                        db_collection=DatabaseCollection.USER_DONE_TASKS,
                        task_status=TaskStatus.DONE)

    response = \
        client.get(f"{get_prefix()}/admin/task",
                   headers={
                       "Authorization": controller.settings.admin_key
                   },
                   query_string={
                       "id": client_id,
                       "task_id": task_id
                   })

    pending_task = response.json.get("pending_tasks")
    sent_tasks = response.json.get("sent_tasks")[0]

    sent_client_task = ClientTask().deserialize(sent_tasks[0])

    assert len(sent_tasks) == 1, "Incorrect number of sent tasks"
    assert len(pending_task) == 0, "Incorrect number of pending tasks"
    assert sent_client_task.id.get('client_id') == client_id, "Client ID does not match"
    assert sent_client_task.get_task_id() == task_id, "Task ID does not match"
    assert sent_client_task.status == TaskStatus.DONE, "Task status does not match"
    assert sent_client_task.status_code == 0, "Status code does not match"


def test_get_task(client):
    """
    Test the /admin/task get endpoint
    :param client:
    :return:
    """
    router.router.controller.db.clear()
    client_id_sent, task_id_sent = randomize_ids()
    client_id_pending, task_id_pending = randomize_ids()

    # Save a task as sent DB
    set_client_and_task(client_id=client_id_sent,
                      task_id=task_id_sent,
                      db_collection=DatabaseCollection.USER_DONE_TASKS,
                      task_status=TaskStatus.DONE)

    # Save a task as pending in DB
    set_client_and_task(client_id=client_id_pending,
                      task_id=task_id_pending,
                      db_collection=DatabaseCollection.USER_TASKS,
                      task_status=TaskStatus.PENDING)

    response = \
        client.get(f"{get_prefix()}/admin/task",
                   headers={
                       "Authorization": controller.settings.admin_key
                   },
                   query_string={
                   })
    pending_tasks = response.json.get("pending_tasks")
    sent_tasks = response.json.get("sent_tasks")[0]

    pending_client_task = ClientTask().deserialize(pending_tasks[0])
    sent_client_task = ClientTask().deserialize(sent_tasks[0])

    assert response.status_code == 200, "Received a non-200 status code"
    assert pending_client_task.get_task_id() == task_id_pending, \
        "Pending task ID does not match"
    assert sent_client_task.get_task_id() == task_id_sent, \
        "Sent task ID does not match"


