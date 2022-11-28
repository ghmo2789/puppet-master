from .models import Client
from decouple import config
import requests
import time


class ControlServerHandler():
    url = ""
    prefix = ""
    authorization = ""

    def __init__(self):
        self.url = config("CONTROL_SERVER_URL")
        self.prefix = config("CONTROL_SERVER_PREFIX")
        self.authorization = config("CONTROL_SERVER_AUTHORIZATION")

    def __save_clients(self, clients):
        # TODO: Old clients will still be visible even if they are not connected
        # Client.objects.all().delete()
        for client in clients:
            if not (Client.objects.filter(client_id=client['_id']).exists()):
                client_data = client['client_data']
                c = Client(client_id=client['_id'],
                           ip=client['ip'],
                           os_name=client_data['os_name'],
                           os_version=client_data['os_version'],
                           hostname=client_data['hostname'],
                           host_user=client_data['host_user'],
                           privileges=client_data['privileges'])
                c.save()

    def getClients(self):
        requestUrl = "https://" + self.url + self.prefix + "/admin/allclients"
        requestHeaders = {'Authorization': self.authorization}
        r = requests.get(url=requestUrl, headers=requestHeaders)
        try:
            clients = r.json()['all_clients']
            self.__save_clients(clients)
            return clients
        except ValueError as e:
            print("Server issues" + str(e))
            return []

    def __saveTask(self, c_id, task_t, task_i):
        client = Client.objects.get(client_id=c_id)
        t = time.localtime()
        asc_t = time.asctime(t)
        client.senttask_set.create(start_time=asc_t, finish_time='ongoing', task_type=task_t, task_info=task_i)

    def sendTasks(self, request):
        client_ids = request.POST.getlist('select')
        task_t = request.POST.getlist('option')[0]
        task_info = "..."
        if task_t == "Write command":
            task_info = request.POST.getlist('text')[0]
            task_info = task_info.replace('"', '\"')
            task_t = "terminal"
        elif task_t == "Open browser":
            task_info = "sensible-browser 'google.com'"
        for c_id in client_ids:
            self.__saveTask(c_id, task_t, task_info)

        client_ids_string = ", ".join(client_ids)
        requestUrl = "https://" + self.url + self.prefix + "/admin/task"
        requestHeaders = {'Authorization': self.authorization}

        data = {
            "client_id": client_ids_string,
            "data": task_info,
            "name": task_t,
            "min_delay": "500",
            "max_delay": "500"
        }

        response = requests.post(url=requestUrl, headers=requestHeaders, json=data)
        status_code = response.status_code
        if status_code == 200:
            print("Tasks sent")
        elif status_code == 400:
            print("No client IDs were given")
        elif status_code == 401:
            print("wrong authorization token")
        elif status_code == 404:
            print("One or more of the clients do not exist")
        else:
            print("Something went very wrong")

        return
