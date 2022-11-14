from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    dummyData = [{'id': 1, 'os': 'linux', 'status': 'ok'},
                 {'id': 2, 'os': 'windows', 'status': 'ok'}]
    context = {'data': dummyData}
    return render(request, 'website/index.html',context)
    #return HttpResponse("Hello world!")
