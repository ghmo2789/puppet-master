from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import clientForm
from .models import Client
from .models import SentTask
import time

def create_task(c_id, task_t):
    client = Client.objects.get(client_id = c_id)
    t = time.localtime()
    asc_t = time.asctime(t)
    task = client.senttask_set.create(start_time=asc_t, finish_time='-', task_type=task_t, task_info="description")

def send_tasks(request):
    client_ids = request.POST.getlist('select')
    task_t = request.POST.getlist('option')[0]
    for c_id in client_ids:
        create_task(c_id, task_t)
    return

def index(request):
    for i in range(1, 23):
        current_client = Client(client_id=i, os="linux", version = 510, host_name="dator", host_user="user", status=True)
        current_client.save()

    new_client = Client(client_id=1337, os="windows", version=10, host_name="dator", host_user="user", status=True)
    new_client.save()
    new_task = new_client.senttask_set.create(start_time=1, finish_time=0, task_type="type", task_info="description") 
   
    tasks = [{'name': "Write command"}, {'name': "Open browser"}, {'name': "Other task"}]
    
    if request.method == 'POST':
        form = clientForm(request.POST)
        if form.is_valid(): 
            send_tasks(request)
    else:
        form = clientForm()

    context = {'clients': Client.objects.all(), 'tasks': tasks, 'form': form}
    return render(request, 'website/index.html', context, )
    #return HttpResponse("Hello world!")
