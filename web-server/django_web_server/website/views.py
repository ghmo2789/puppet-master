from django.shortcuts import render
from .forms import clientForm
from .models import Client
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
    return


def index(request):
    for i in range(1, 23):
        current_client = Client(client_id=i, os="linux", version=510, host_name="dator", host_user="user", status=True)
        current_client.save()

    tasks = [{'name': "Write command"}, {'name': "Open browser"}, {'name': "Other task"}]

    if request.method == 'POST':
        form = clientForm(request.POST)
        if form.is_valid():
            send_tasks(request)
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
               'locations': json.dumps(dummyLocations)}

    return render(request, 'website/index.html', context, )


def tasks(request):
    context = {'data': 'hello tasks'}
    return render(request, 'website/tasks.html', context)
