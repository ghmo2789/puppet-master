from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from .forms import clientForm
from .models import Client, SentTask
from .filters import ClientFilter, TaskFilter
from .server import ControlServerHandler
import json


def index(request):
    """
    Front-page and client-page view
    :param request: Request object
    :side effects: Loads all clients from the control server into the
                   database. If the request is a POST request, it will send
                   task corresponding to the form to the control server
    :return: Rendering of the client webpage
    """
    controlServer = ControlServerHandler()
    controlServer.getClients()
    controlServer.getTasks()
    tasks = [{'name': "Write command"}, {'name': "Scan network"}]

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

    clients = Client.objects.all()

    context = {'clients': Client.objects.all(),
               'tasks': tasks,
               'form': form,
               'statistics': statistics,
               'locations': json.dumps(locations),
               'filter': ClientFilter(request.GET, queryset=Client.objects.all())}

    return render(request, 'website/index.html', context, )


def tasks(request):
    """
    Tasks-page view
    :param request: Request object
    :side effects: Loads all tasks from the control server into the
                   database. If the request is a POST, it will send 
                   abort task to the control server
    :return: Rendering of the tasks webpage
    """
    controlServer = ControlServerHandler()
    controlServer.getClients()
    controlServer.getTasks()

    if request.method == 'POST':
        controlServer.killTask(request)
        return HttpResponseRedirect(request.path_info)
    context = {'tasks': TaskFilter(request.GET, queryset=SentTask.objects.all().order_by('-id'))}
    return render(request, 'website/tasks.html', context)


def task_output(request):
    """
    Gets task output of a specific task from the control server
    :param request: Request object containing task info
    :return: The task output
    """
    controlServer = ControlServerHandler()
    task_id = json.loads(request.body)['task_id']
    client_id = task_id[36:72]
    task_id = task_id[0:36]
    output = controlServer.getTaskOutput(task_id, client_id)
    taskOutput = {
        'output': output,
    }
    return JsonResponse(taskOutput)


def updated_tasks(request):
    """
    Gets all tasks from the control server in order to update their status
    :param request: Request object
    :side effects: Gets all tasks from the control server and updates their
                   status in the database if it has changed
    :return: List of the ids and new status of the tasks which has been updated
    """
    controlServer = ControlServerHandler()
    updatedTaskStatus = controlServer.getUpdatedTaskStatus()
    updatedTaskList = {
        'tasks': updatedTaskStatus
    }

    return JsonResponse(updatedTaskList)


def updated_client_status(request):
    """
    Gets all clients from the control server and updates their last seen timestamp
    :param request: Request object
    :side effects: Gets all clients from the control server and updates in
                   the database the date and time they were last seen 
    :return: List of the ids and timestamps of the clients that has been updated
    """
    controlServer = ControlServerHandler()
    updatedclientStatus = controlServer.getUpdatedClientStatus()
    updatedClientList = {
        'clients': updatedclientStatus
    }

    return JsonResponse(updatedClientList)
