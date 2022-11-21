from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import clientForm

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
    
    tasks = [{'name': "Write command"}, {'name': "Open browser"}, {'name': "Other task"}]
    
    if request.method == 'POST':
        print(request.POST)
        form = clientForm(request.POST)
        if form.is_valid():
            print("hej")
    else:
        form = clientForm()
        print("nej")    

    context = {'data': dummyData, 'tasks': tasks, 'form': form}
    return render(request, 'website/index.html', context, )
    #return HttpResponse("Hello world!")
