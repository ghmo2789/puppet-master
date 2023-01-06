from django.test import TestCase, RequestFactory
from .models import Client, SentTask
from datetime import datetime
from .server import ControlServerHandler
from unittest.mock import Mock, patch


class FirstTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.controlServer = ControlServerHandler()
        self.mock_client_id = 'b412387f-b8c6-922b-0a2e-df8631b6977f'
        self.mock_task_id = 'c7dedc0d-f1cb-4554-960d-a94200092562'
        Client.objects.create(client_id=self.mock_client_id, ip='1.1.1.1',
                              os_name='mac', os_version='1', hostname='pelle',
                              host_user='kjelle', privileges='admin',
                              first_seen_date='2022-12-10', first_seen_time='12:00:00',
                              first_seen_datetime=datetime.strptime('2022-12-10T12:00:00', '%Y-%m-%dT%H:%M:%S'),
                              last_seen_date='2023-01-01', last_seen_time='13:00:00', is_online=True,
                              time_since_last_seen=1111111)
        client = Client.objects.get(client_id=self.mock_client_id)
        client.senttask_set.create(task_id=self.mock_task_id+self.mock_client_id, start_time='2023-01-01T14:00:00',
                                   start_time_datetime=datetime.strptime('2023-01-01T14:00:00', '%Y-%m-%dT%H:%M:%S'),
                                   status='pending', task_type='Write command', task_info='ls')

        self.get_all_clients_response = {
            'all_clients': [{'_id': '072c1330-c4d7-bb7b-6c36-dfa92d8b456e',
                             'client_data': {'host_id': 'B105E735-5C8D-54A1-BB8E-7A6F41790F12',
                                             'host_user': 'izaalstergren',
                                             'hostname': 'izas-mbp',
                                             'os_name': 'Mac',
                                             'os_version': 'OS',
                                             'polling_time': 10,
                                             'privileges': 'null'},
                             'first_seen': '2022-12-20T13:13:21.533301+01:00',
                             'ip': '92.34.135.80',
                             'is_online': False,
                             'last_seen': '2023-01-04T18:38:06.664175+01:00',
                             'time_since_last_seen': 55421.560754}]}

        self.get_task_output_response = {
            'task_responses': [{'_id': {'client_id': '4aee4944-939d-350f-9c20-2d23c311ed7e',
                                        'task_id': 'b7dedc0d-f1cb-4554-960d-a94200092562'},
                                'responses': [{'id': 'b7dedc0d-f1cb-4554-960d-a94200092562',
                                               'result': 'Cargo.lock\nCargo.toml\nDockerfile' +
                                                         '\ndocker-compose.yml\nsample.env\n' +
                                                         'src\nstart-docker-container.sh\ntarget' +
                                                         '\ntest\n',
                                               'status': 0,
                                               'time': '2022-12-22T13:47:28.807677+01:00'}]}]}
        self.ip_convert_response = {
            'status': 'success',
            'country': 'Australia',
            'countryCode': 'AU',
            'region': 'QLD',
            'regionName': 'Queensland',
            'city': 'South Brisbane',
            'zip': '4101',
            'lat': -27.4766,
            'lon': 153.0166,
            'timezone': 'Australia/Brisbane',
            'isp': 'Cloudflare, Inc',
            'org': 'APNIC and Cloudflare DNS Resolver project',
            'as': 'AS13335 Cloudflare, Inc.',
            'query': '1.1.1.1'}

        self.get_tasks_response = {
            'pending_tasks': [{'_id': {'client_id': self.mock_client_id,
                                       'task_id': 'fb053b6e-ad2f-4335-9f1c-3b1e40e6fd47'},
                               'status': 'pending',
                               'status_code': -2,
                               'status_update_time': None,
                               'task': {'created_time': '2023-01-04T13:31:34.837271+01:00',
                                        'data': 'cat',
                                        'id': 'fb053b6e-ad2f-4335-9f1c-3b1e40e6fd47',
                                        'max_delay': 500,
                                        'min_delay': 500,
                                        'name': 'terminal'}}],
            'sent_tasks': [[{'_id': {'client_id': self.mock_client_id,
                                     'task_id': '5a7a4aec-684b-45b0-8d72-a1d0a74d6d9f'},
                             'status': 'in progress',
                             'status_code': 0,
                             'status_update_time': '2022-12-19T07:48:26.688732+01:00',
                             'task': {'created_time': '2022-12-19T07:48:14.782341+01:00',
                                      'data': 'ls',
                                      'id': '5a7a4aec-684b-45b0-8d72-a1d0a74d6d9f',
                                      'max_delay': 500,
                                      'min_delay': 500,
                                      'name': 'terminal'}}]]}

        self.get_updated_tasks_response = {
            'pending_tasks': [],
            'sent_tasks': [[{'_id': {'client_id': self.mock_client_id,
                                     'task_id': self.mock_task_id},
                             'status': 'done',
                             'status_code': 0,
                             'status_update_time': '2022-12-19T07:48:26.688732+01:00',
                             'task': {'created_time': '2022-12-19T07:48:14.782341+01:00',
                                      'data': 'ls',
                                      'id': '5a7a4aec-684b-45b0-8d72-a1d0a74d6d9f',
                                      'max_delay': 500,
                                      'min_delay': 500,
                                      'name': 'terminal'}}]]}

    def test_setup(self):
        c = Client.objects.get(client_id=self.mock_client_id)
        num_c = Client.objects.all().count()
        self.assertEqual(c.ip, '1.1.1.1')
        self.assertEqual(num_c, 1)

    @patch('website.server.requests.get')
    def test_get_all_clients(self, mock_get):
        mock_get.return_value.ok = True
        self.controlServer.getClients()
        num_c = Client.objects.all().count()
        self.assertEqual(num_c, 1)

    @patch('website.server.requests.get')
    def test_get_task_output(self, mock_get):
        mock_response = self.get_task_output_response
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = mock_response
        expected_result = "Cargo.lock<br>Cargo.toml<br>Dockerfile<br>" +\
                          "docker-compose.yml<br>sample.env<br>src<br>" +\
                          "start-docker-container.sh<br>target<br>test<br>"
        result = self.controlServer.getTaskOutput('b7dedc0d-f1cb-4554-960d-a94200092562',
                                                  '4aee4944-939d-350f-9c20-2d23c311ed7e')
        self.assertEqual(expected_result, result)

    @patch('website.server.requests.get')
    def test_get_clients(self, mock_get):
        mock_response = self.get_all_clients_response
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = mock_response

        self.controlServer.getClients()
        num_c = Client.objects.all().count()
        first_c = Client.objects.all()[0]

        self.assertEqual(num_c, 1)
        self.assertEqual(first_c.ip, '92.34.135.80')

    @patch('website.server.requests.get')
    def test_get_clients_update_status(self, mock_get):
        mock_response = self.get_all_clients_response
        mock_response['all_clients'][0]['last_seen'] = '2023-01-01T15:00:00.664175+01:00'
        mock_response['all_clients'][0]['_id'] = self.mock_client_id
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = mock_response

        self.controlServer.getUpdatedClientStatus()
        num_c = Client.objects.all().count()
        first_c = Client.objects.all()[0]

        self.assertEqual(num_c, 1)
        self.assertEqual(first_c.last_seen_date, '2023-01-01')
        self.assertEqual(first_c.last_seen_time, '15:00:00')

    def test_get_statistics(self):
        statistics = self.controlServer.getStatistics()
        expected_statistics = {
            'client_stats': {'num_clients': 1,
                             'num_online': 1,
                             'num_offline': 0},
            'task_stats': {'num_pending': 1,
                           'num_in_progress': 0,
                           'num_done': 0,
                           'num_aborted': 0,
                           'num_error': 0},
            'oldest_task_running': {'exists': False,
                                    'task_id': '',
                                    'time_since_started': ''}}

        self.assertEqual(statistics, expected_statistics)

    @patch('website.server.requests.get')
    def test_get_locations(self, mock_get):
        mock_response = self.ip_convert_response
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = mock_response
        result = self.controlServer.getLocations()
        expected_result = [{'client_ids': [1], 'location': [-27.4766, 153.0166]}]

        self.assertEqual(result, expected_result)

    @patch('website.server.requests.post')
    def test_send_task(self, mock_post):
        web_request_data = {'csrfmiddlewaretoken': ['a7OPCwZKzLjCJ42NGwNNlJYYDK52S1EE6VPFcaGdnp9nDN3DB8LqsnAPWJpnRSMA'],
                            'select': ['072c1330-c4d7-bb7b-6c36-dfa92d8b456e'],
                            'option': ['Write command'],
                            'text': ['ls']}
        web_request = self.factory.post('/website/clients', web_request_data)
        mock_post.return_value = Mock(ok=True, status_code=200)
        response = self.controlServer.sendTasks(web_request)

        self.assertEqual(response.status_code, 200)

    @patch('website.server.requests.get')
    def test_get_tasks(self, mock_get):
        mock_response = self.get_tasks_response
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = mock_response
        self.controlServer.getTasks()

        num_t = SentTask.objects.all().count()
        self.assertEqual(num_t, 3)

    @patch('website.server.requests.get')
    def test_get_updated_task_status(self, mock_get):
        mock_response = self.get_updated_tasks_response
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = mock_response

        updated_task_status = self.controlServer.getUpdatedTaskStatus()

        self.assertEqual(len(updated_task_status), 1)
        self.assertEqual(updated_task_status[0]['new_status'], 'done')

    @patch('website.server.requests.post')
    def test_kill_task(self, mock_post):
        web_request_data = {'csrfmiddlewaretoken': ['XToMoUvupkT7uaSIMKXDooyAjdKwqZK8THpCYycXdYJSoTTyHmVgv2arCc4RpQS4'],
                            'abort': ['1']}
        web_request = self.factory.post('/website/tasks', web_request_data)
        mock_post.return_value = Mock(ok=True, status_code=200)
        response = self.controlServer.killTask(web_request)

        self.assertEqual(response.status_code, 200)

    def test_client_str(self):
        c = Client.objects.all()[0]
        self.assertEqual(str(c), 'Id: b412387f-b8c6-922b-0a2e-df8631b6977f')

    def test_client_first_seen_time_str(self):
        c = Client.objects.all()[0]
        self.assertEqual(c.first_seen_time_str(), '12:0:0')

    def test_client_str_last_seen(self):
        c = Client.objects.all()[0]
        self.assertEqual(c.str_last_seen(), '12 days 20 hours 38 minutes ')

    def test_senttask_start_time_str(self):
        t = SentTask.objects.all()[0]
        self.assertEqual(t.start_time_str(), '14:0:0')

    def test_senttask_str(self):
        t = SentTask.objects.all()[0]
        self.assertEqual(str(t), 'task id = c7dedc0d-f1cb-4554-960d-a94200092562b412387f-b8c6-922b-0a2e-df8631b6977f')
