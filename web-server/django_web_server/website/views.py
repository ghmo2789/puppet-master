from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json


def index(request):
    dummyData = [{'id': 1, 'os': 'linux', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 3, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 4, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 5, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 6, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 7, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 8, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 9, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 10, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 11, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 12, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 13, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 14, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 15, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 16, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 17, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 18, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 19, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 20, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 21, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 22, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'},
                 {'id': 23, 'os': 'windows', 'version': '5.1', 'hostname': 'skoldator', 'host_user': 'Alfred', 'status': 'ok'}]

    dummyStatistics = {'num_clients': 23,
                       'top_os': 'windows',
                       'errors': 0}

    dummyLocations = {'locations': [[0, 0], [51.5, -0.09], [-0.09, 51.5]]}

    context = {'data': dummyData,
               'statistics': dummyStatistics,
               'locations' : json.dumps(dummyLocations)}
    return render(request, 'website/index.html',context)

def tasks(request):
    dummyTasks = [{'taskId': 1, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 2, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 3, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 4, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 5, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 6, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 7, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 8, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 9, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 10, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 11, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 12, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 13, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 14, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 15, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 16, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  {'taskId': 17, 'clientId': 1, 'start': 1230, 'finish': 1259, 'status': 'finished', 'taskType': 'bash', 'taskInfo': 'echo hello'},
                  ]
    
    formStatus = 'Button not pressed'

    if request.method == 'POST':
        formStatus = 'Button was pressed!'

    context = {'data': dummyTasks,
               'formStatus': formStatus}
    return render(request, 'website/tasks.html', context)
    
    return tasks(request)

def kill_task(request):
    return tasks(request)
