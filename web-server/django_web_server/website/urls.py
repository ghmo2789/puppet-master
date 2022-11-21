from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('clients', views.index, name='clients'),
    path('tasks', views.tasks, name='tasks'),
    path('kill_task', views.kill_task, name='kill_task'),
]