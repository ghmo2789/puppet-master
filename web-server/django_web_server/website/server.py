from .models import Client, SentTask
from decouple import config
import requests
import json

class ControlServerHandler():
    url = ""
    prefix = ""
    authorization = ""

    def __init__(self):
        # url = config("CONTROL_SERVER_URL")
        # prefix = config("CONTROL_SERVER_PREFIX")
        # authorization = config("CONTROL_SERVER_AUTHORIZATION")

        self.url = "1dl650.rickebo.com"
        self.prefix = "/control"
        self.authorization = "2aa3a0d9be45175b1628d5ec8c487da81f9df6432b0b5429a1d73e4e3b84b459"
    
    def __save_clients(self, clients):
        for client in clients:
            client_data = client['client_data']
            c = Client(_id = client['_id'],
                       ip = client['ip'],
                       os_name = client_data['os_name'],
                       os_version = client_data['os_version'],
                       hostname = client_data['hostname'],
                       host_user = client_data['host_user'],
                       privileges = client_data['privileges'])
            c.save()


    def getClients(self):
        requestUrl = "https://" + self.url + self.prefix + "/admin/allclients"
        requestHeaders = {'Authorization': self.authorization}
        r = requests.get(url = requestUrl, headers = requestHeaders)
        clients = r.json()['all_clients']
        #clients = json.load(clientsJson)
        self.__save_clients(clients)

        return clients

      