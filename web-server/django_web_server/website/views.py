from django.shortcuts import render
from .forms import clientForm
from .models import Client, SentTask
from .filters import ClientFilter
from .server import ControlServerHandler
import json
import time


def create_task(c_id, task_t):
    client = Client.objects.get(client_id=c_id)
    t = time.localtime()
    asc_t = time.asctime(t)
    client.senttask_set.create(start_time=asc_t, finish_time='-', task_type=task_t, task_info="description")


def send_tasks(request):
    client_ids = request.POST.getlist('select')
    task_t = request.POST.getlist('option')[0]
    for c_id in client_ids:
        create_task(c_id, task_t)
    # TODO: Send to control server
    return


def kill_task(request):
    # TODO: Send to control server
    return


def index(request):
    controlServer = ControlServerHandler()
    controlServer.getClients()

    tasks = [{'name': "Write command"}, {'name': "Open browser"}, {'name': "Other task"}]

    if request.method == 'POST':
        form = clientForm(request.POST)
        if form.is_valid():
            send_tasks(request)
    else:
        form = clientForm()

    statistics = controlServer.getStatistics()
    coordinates = controlServer.getLocations()
    locations = {'locations': coordinates}

    context = {'clients': Client.objects.all(),
               'tasks': tasks,
               'form': form,
               'statistics': statistics,
               'locations': json.dumps(locations),
               'filter': ClientFilter(request.GET, queryset=Client.objects.all())}

    return render(request, 'website/index.html', context, )


def tasks(request):
    if request.method == 'POST':
        kill_task(request)

    context = {'tasks': SentTask.objects.all()[:200]}
    return render(request, 'website/tasks.html', context)
