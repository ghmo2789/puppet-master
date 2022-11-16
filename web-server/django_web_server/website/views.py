from django.shortcuts import render
from django.http import HttpResponse
import json


def index(request):
    dummyData = [{'id': 1, 'os': 'linux', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'}]

    dummyStatistics = {'num_clients': 23,
                       'top_os': 'windows',
                       'errors': 0}

    dummyLocations = {'locations': [[0, 0], [51.5, -0.09], [-0.09, 51.5]]}

    context = {'data': dummyData,
               'statistics': dummyStatistics,
               'locations' : json.dumps(dummyLocations)}
    return render(request, 'website/index.html',context)
