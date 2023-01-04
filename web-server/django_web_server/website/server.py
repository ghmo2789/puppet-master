from decouple import config
import requests
from .models import Client, SentTask
from datetime import datetime
from django.utils.timezone import make_aware


class ControlServerHandler():
    """
    A Class for handling all the communication with the control server
    """

    url = ""
    prefix = ""
    authorization = ""
    errors = 0

    def __init__(self):
        self.url = config("CONTROL_SERVER_URL")
        self.prefix = config("CONTROL_SERVER_PREFIX")
        self.authorization = config("CONTROL_SERVER_AUTHORIZATION")

    def __save_clients(self, clients):
        """
        Saves clients and their information in the database
        :param clients: List of clients
        :side effects: Saves clients in the database if they do not already exist,
                       otherwise update their status. If a client in the database no
                       longer exists in the control server it will be deleted
        :return:
        """
        saved_client_ids = list(Client.objects.values_list('client_id', flat=True))
        received_client_ids = [client['_id'] for client in clients]

        for saved_client in saved_client_ids:
            if saved_client not in received_client_ids:
                Client.objects.filter(client_id=saved_client).delete()

        for client in clients:
            if not (Client.objects.filter(client_id=client['_id']).exists()):
                client_data = client['client_data']
                first_seen = client['first_seen']
                first_seen_trunc = first_seen[0:19]
                first_seen_dt = datetime.strptime(first_seen_trunc, '%Y-%m-%dT%H:%M:%S')
                aware_first_seen_dt = make_aware(first_seen_dt)
                c = Client(client_id=client['_id'],
                           ip=client['ip'],
                           os_name=client_data['os_name'],
                           os_version=client_data['os_version'],
                           hostname=client_data['hostname'],
                           host_user=client_data['host_user'],
                           privileges=client_data['privileges'],
                           first_seen_date=client['first_seen'][0:10],
                           first_seen_time=client['first_seen'][11:19],
                           first_seen_datetime=aware_first_seen_dt,
                           last_seen_date=client['last_seen'][0:10],
                           last_seen_time=client['last_seen'][11:19],
                           is_online=client['is_online'],
                           time_since_last_seen=client['time_since_last_seen'])
                c.save()
            else:
                Client.objects.filter(client_id=client['_id']) \
                              .update(last_seen_date=client['last_seen'][0:10],
                                      last_seen_time=client['last_seen'][11:19],
                                      is_online=client['is_online'],
                                      time_since_last_seen=client['time_since_last_seen'])

    def getClients(self):
        """
        Send request to control server to retrieve all clients and saves
        them in the database
        :side effects: Saves clients in the database if they do not already exist,
                       otherwise update their status. If a client in the database no
                       longer exists in the control server it will be deleted
        :return:
        """
        requestUrl = "https://" + self.url + self.prefix + "/admin/allclients"
        requestHeaders = {'Authorization': self.authorization}
        r = requests.get(url=requestUrl, headers=requestHeaders)
        if r.status_code == 200:
            try:
                clients = r.json()['all_clients']
                self.__save_clients(clients)
                return clients
            except ValueError as e:
                print("Server issues" + str(e))
                return []
        if r.status_code == 404:
            Client.objects.all().delete()

    def getStatistics(self):
        """
        Gathers statistics about the clients and tasks
        :return: Statistics containing the number of clients, number online/offline,
                 number of task in of each status and the longing running task
        """
        num_clients = Client.objects.all().count()
        num_online = Client.objects.filter(is_online=True).count()
        num_offline = Client.objects.filter(is_online=False).count()
        client_stats = {
            'num_clients': num_clients,
            'num_online': num_online,
            'num_offline': num_offline
        }

        num_pending = SentTask.objects.filter(status='pending').count()
        num_in_progress = SentTask.objects.filter(status='in progress').count()
        num_aborted = SentTask.objects.filter(status='aborted').count()
        num_done = SentTask.objects.filter(status='done').count()
        num_error = SentTask.objects.filter(status='error').count()
        task_stats = {
            'num_pending': num_pending,
            'num_in_progress': num_in_progress,
            'num_done': num_done,
            'num_aborted': num_aborted,
            'num_error': num_error,
        }

        oldest_task_running = {}
        if num_in_progress > 0:
            oldest_task_running_obj = SentTask.objects.filter(status='in progress').order_by('start_time_datetime')[0]
            oldest_task_running = {
                'exists': True,
                'task_id': oldest_task_running_obj.id,
                'time_since_started': oldest_task_running_obj.time_since_started()
            }
        else:
            oldest_task_running = {
                'exists': False,
                'task_id': '',
                'time_since_started': '',
            }

        statistics = {
            'client_stats': client_stats,
            'task_stats': task_stats,
            'oldest_task_running': oldest_task_running
        }

        return statistics

    def getLocations(self):
        """
        Gets the lat, long location of each client
        :side effects: Calls an external API for converting IP address to lat, long location
        :return: List of locations containing its lat, long coordinates and all clients
                 which are connected from that location
        """
        ids = list(Client.objects.values_list('id', flat=True))
        locations = []

        for c_id in ids:
            try:
                ip = Client.objects.get(id=c_id).ip
                requestUrl = 'http://ip-api.com/json/' + ip
                r = requests.get(url=requestUrl)
                if r.status_code == 200:
                    response = r.json()
                    lat = response['lat']
                    lon = response['lon']
                    clientLocation = {
                        'client': c_id,
                        'location': [lat, lon],
                    }
                    locations.append(clientLocation)
            except Exception as e:
                print(f'IP could not be converted to location: {e}')

        summarized_locations = []
        processed_locations = []

        for client_location in locations:
            client_ids = [client_location['client']]
            current_loc = client_location['location']

            if current_loc not in processed_locations:
                for cl in locations:
                    if current_loc == cl['location'] and cl['client'] not in client_ids:
                        client_ids.append(cl['client'])

                summarized_location = {
                    'client_ids': client_ids,
                    'location': current_loc
                }

                summarized_locations.append(summarized_location)
                processed_locations.append(current_loc)

        return summarized_locations

    def __saveTask(self, t_id, c_id, task_t, task_i, t_status, t_start_time, t_start_time_dt):
        """
        Saves a task in the database
        :param t_id: The task id
        :param c_id: The client id of the client running the task
        :param task_t: The task type
        :param task_i: The task information
        :param t_status: The task status
        :param t_start_time: The task start time represented as a string
        :param t_start_time_dt: The task start time represented as a datetime object
        :side effects: Saves the task in the database
        """
        if task_t != 'abort':
            client = Client.objects.get(client_id=c_id)
            client.senttask_set.create(task_id=t_id, start_time=t_start_time, start_time_datetime=t_start_time_dt,
                                       status=t_status, task_type=task_t, task_info=task_i)

    def getTaskOutput(self, task_id, client_id):
        """
        Gets output for a task from the control server
        :param task_id: The task id
        :param client_id: The client id of the client running the task
        :return: Returns the task output in a string
        """
        output_string = ""
        requestUrl = "https://" + self.url + self.prefix + "/admin/taskoutput"
        requestHeaders = {'Authorization': self.authorization}
        data = {
            "id": str(client_id),
            "task_id": str(task_id),
        }
        response = requests.get(url=requestUrl, headers=requestHeaders, params=data)
        status_code = response.status_code
        if status_code == 200 and response.json() != {'task_responses': []}:
            output_string = str(response.json()['task_responses'][0]['responses'][0]['result']).replace("\n", "<br>")
        return output_string

    def getTasks(self):
        """
        Gets all tasks from the control server
        :side effects: Saves all the tasks in the database
        :return:
        """
        requestUrl = "https://" + self.url + self.prefix + "/admin/task"
        requestHeaders = {'Authorization': self.authorization}

        data = {
            "id": "",
        }
        response = requests.get(url=requestUrl, headers=requestHeaders, params=data)

        status_code = response.status_code
        if status_code == 200:
            # If there are no clients saved, get them first
            if Client.objects.all().count() == 0:
                self.getClients()
            pending_tasks = response.json()['pending_tasks']
            sent_tasks = response.json()['sent_tasks'][0]
            for task in pending_tasks:
                t_id = task['_id']['task_id'] + task['_id']['client_id']
                c_id = task['_id']['client_id']
                # Create new task only if task does not already exist and its client exists
                if (not (SentTask.objects.filter(task_id=t_id).exists())) \
                   and Client.objects.filter(client_id=c_id).exists():
                    task_t = task['task']['name']
                    task_i = task['task']['data']
                    t_status = 'pending'
                    start_time = task['task']['created_time']
                    start_time_trunc = start_time[0:19]
                    start_time_dt = datetime.strptime(start_time_trunc, '%Y-%m-%dT%H:%M:%S')
                    aware_start_time_dt = make_aware(start_time_dt)
                    self.__saveTask(t_id, c_id, task_t, task_i, t_status, start_time, aware_start_time_dt)
            for task in sent_tasks:
                t_id = task['_id']['task_id'] + task['_id']['client_id']
                c_id = task['_id']['client_id']
                # Create new task only if task does not already exist and its client exists
                if (not (SentTask.objects.filter(task_id=t_id).exists())) \
                   and Client.objects.filter(client_id=c_id).exists():
                    task_t = task['task']['name']
                    task_i = task['task']['data']
                    t_status = task['status'].replace("_", " ")
                    start_time = task['task']['created_time']
                    start_time_trunc = start_time[0:19]
                    start_time_dt = datetime.strptime(start_time_trunc, '%Y-%m-%dT%H:%M:%S')
                    aware_start_time_dt = make_aware(start_time_dt)
                    self.__saveTask(t_id, c_id, task_t, task_i, t_status, start_time, aware_start_time_dt)
                else:
                    SentTask.objects.filter(task_id=t_id).update(status=task['status'].replace("_", " "))

    def getUpdatedTaskStatus(self):
        """
        Gets all updated tasks and their new status
        :side effects: Updates the task status in the database
        :return: A list of updated tasks with their id and new status
        """
        requestUrl = "https://" + self.url + self.prefix + "/admin/task"
        requestHeaders = {'Authorization': self.authorization}

        data = {
            "id": "",
        }
        response = requests.get(url=requestUrl, headers=requestHeaders, params=data)

        updated_tasks = []

        status_code = response.status_code
        if status_code == 200:
            sent_tasks = response.json()['sent_tasks'][0]
            for task in sent_tasks:
                t_id = task['_id']['task_id'] + task['_id']['client_id']
                if (SentTask.objects.filter(task_id=t_id).exists()):
                    t_sent_status = task['status'].replace("_", " ")
                    t_current_status = SentTask.objects.get(task_id=t_id).status
                    if t_sent_status != t_current_status:
                        our_id = SentTask.objects.get(task_id=t_id).id
                        SentTask.objects.filter(task_id=t_id).update(status=t_sent_status)
                        new_updated_task = {
                            'id': our_id,
                            'task_id': t_id,
                            'new_status': t_sent_status
                        }
                        updated_tasks.append(new_updated_task)

        return updated_tasks

    def getUpdatedClientStatus(self):
        """
        Gets all updated clients and their new time for last seen
        :return: A list of updated clients with their new time last seen
        """
        requestUrl = "https://" + self.url + self.prefix + "/admin/allclients"
        requestHeaders = {'Authorization': self.authorization}
        r = requests.get(url=requestUrl, headers=requestHeaders)

        try:
            clients = r.json()['all_clients']
            updated_clients = []
            for client in clients:
                client_id = client['_id']
                new_last_seen_date = client['last_seen'][0:10]
                new_last_seen_time = client['last_seen'][11:19]
                if (Client.objects.filter(client_id=client_id).exists()):
                    c = Client.objects.get(client_id=client_id)
                    if c.last_seen_date != new_last_seen_date or c.last_seen_time != new_last_seen_time:
                        c.last_seen_date = new_last_seen_date
                        c.last_seen_time = new_last_seen_time
                        new_c = {
                            'client_id': client_id,
                            'new_last_seen_date': new_last_seen_date,
                            'new_last_seen_time': new_last_seen_time
                        }
                        updated_clients.append(new_c)
            return updated_clients
        except ValueError as e:
            print("Server issues" + str(e))
            return []

    def sendTasks(self, request):
        """
        Send tasks to the control server
        :param request: Request object containing information about client ids,
                        task type and task info
        :side effects: Sends post request to control server to send a task
        :return:
        """
        client_ids = request.POST.getlist('select')
        task_t = request.POST.getlist('option')[0]
        task_info = "..."
        if task_t == "Write command":
            task_info = request.POST.getlist('text')[0]
            task_info = task_info.replace('"', '\"')
            task_t = "terminal"
        elif task_t == "Scan network":
            task_t = "network_scan"
            task_info = ""
        elif task_t == "SSH Spread":
            task_t = "ssh_spread"
            task_info = ""

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
        selected = request.POST.getlist('abort')
        task_ids = list(SentTask.objects.filter(id__in=selected).values_list('task_id', flat=True))
        selected_client_ids = list(SentTask.objects.filter(task_id__in=task_ids).values_list('client_id', flat=True))
        client_ids = list(Client.objects.filter(id__in=selected_client_ids).values_list('client_id', flat=True))
        true_task_ids = [id[:len(id)//2] for id in task_ids]

        requestUrl = "https://" + self.url + self.prefix + "/admin/task"
        requestHeaders = {'Authorization': self.authorization}

        client_ids_str = (', ').join(client_ids)
        task_ids_str = (',').join(true_task_ids)

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
