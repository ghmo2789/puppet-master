from control_server.tests.utils.generic_test_utils import get_prefix
from control_server.src.controller import controller
from control_server.src.data.task import Task
from control_server.src.data.client_task import ClientTask
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.data.task_status import TaskStatus
from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import IdentifyingClientData


def set_user_and_task(client_id: str, task_id: str, db_collection: DatabaseCollection):
    """
    Helper function for setting a user and task in the database
    """

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
    client_task.set_status(status=TaskStatus.DONE)
    client_task.set_status_code(status_code=0)

    # Set user in DB
    client_1 = {
        "os_name": "1",
        "os_version": "1",
        "hostname": "1",
        "host_user": "1",
        "privileges": "1",
    }
    data = ClientData.load_from_dict(client_1, raise_error=True)
    new_client = IdentifyingClientData(
        client_data=data,
        ip=client_id
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

    assert response.status_code == 401


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

    assert response.status_code == 404


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

    assert response.status_code == 404


def test_get_task_pending_tasks(client):
    """
    Test the /admin/task get endpoint with pending task
    :param client:
    :return:
    """
    client_id = "1966283-b9b8-4503-a431-6bc39046481f"
    task_id = "1966284-b9b8-4543-a431-6bc39046481f"

    no_task_response = client.get(f"{get_prefix()}/admin/task",
                                  headers={
                                      "Authorization": controller.settings.admin_key
                                  },
                                  query_string={
                                      "id": client_id,
                                      "task_id": task_id
                                  })

    assert no_task_response.status_code == 404

    # Insert a user and task in the DB
    set_user_and_task(client_id=client_id,
                      task_id=task_id,
                      db_collection=DatabaseCollection.USER_TASKS)

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

    assert len(sent_tasks) == 1
    assert len(pending_tasks) == 1
    assert pending_client_task.id.get('client_id') == client_id
    assert pending_client_task.id.get('task_id') == task_id
    assert pending_client_task.status == TaskStatus.DONE
    assert pending_client_task.status_code == 0
    assert pending_client_task.get_task_id() == task_id


def test_get_task_sent_tasks(client):
    """
    Test the /admin/task get endpoint with sent task
    :param client:
    :return:
    """
    client_id = "1966283-b9b8-4503-a431-6bc39046481f"
    task_id = "1966284-b9b8-4543-a431-6bc39046481f"

    no_task_response = client.get(f"{get_prefix()}/admin/task",
                                  headers={
                                      "Authorization": controller.settings.admin_key
                                  },
                                  query_string={
                                      "id": client_id,
                                      "task_id": task_id
                                  })

    assert no_task_response.status_code == 404

    # Insert a user and task in the DB
    set_user_and_task(client_id=client_id,
                      task_id=task_id,
                      db_collection=DatabaseCollection.USER_DONE_TASKS)

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

    assert len(sent_tasks) == 1
    assert len(pending_task) == 0
    assert sent_client_task.id.get('client_id') == client_id
    assert sent_client_task.id.get('task_id') == task_id
    assert sent_client_task.status == TaskStatus.DONE
    assert sent_client_task.status_code == 0
    assert sent_client_task.get_task_id() == task_id


def test_get_task(client):
    """
    Test the /admin/task get endpoint
    :param client:
    :return:
    """
    client_id = "1966283-b9b8-4503-a431-6bc39046481f"
    task_id_sent = "1966284-b9b8-4543-a431-6bc39046482f"
    task_id_pending = "1966284-b9b8-4543-a431-6bc39046483f"

    # Save a task as pending in DB
    set_user_and_task(client_id=client_id,
                      task_id=task_id_pending,
                      db_collection=DatabaseCollection.USER_TASKS)

    # Save a task as sent DB
    set_user_and_task(client_id=client_id,
                      task_id=task_id_sent,
                      db_collection=DatabaseCollection.USER_DONE_TASKS)

    response = \
        client.get(f"{get_prefix()}/admin/task",
                   headers={
                       "Authorization": controller.settings.admin_key
                   },
                   query_string={
                       "id": client_id,
                   })
    pending_tasks = response.json.get("pending_tasks")
    sent_tasks = response.json.get("sent_tasks")[0]

    pending_client_task = ClientTask().deserialize(pending_tasks[0])
    sent_client_task = ClientTask().deserialize(sent_tasks[0])

    assert len(pending_tasks) == 1
    assert len(sent_tasks) == 1
    assert pending_client_task.get_task_id() == task_id_pending
    assert sent_client_task.get_task_id() == task_id_sent
    assert response.status_code == 200
