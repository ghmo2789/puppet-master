from django.shortcuts import render
from django.http import HttpResponse


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

    context = {'data': dummyData,
               'statistics': dummyStatistics}
    return render(request, 'website/index.html',context)
