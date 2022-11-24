from django.db.models import Count
from .models import Client
from decouple import config
import requests
from django.contrib.gis.geoip2 import GeoIP2 


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



