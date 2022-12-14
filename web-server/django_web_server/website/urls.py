from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('clients', views.index, name='clients'),
    path('tasks', views.tasks, name='tasks'),
    path('updated_task', views.updated_tasks, name='updated_tasks'),
    path('updated_client_status', views.updated_client_status, name='updated_client_status')
]
