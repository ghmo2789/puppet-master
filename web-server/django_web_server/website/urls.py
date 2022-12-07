from django.urls import path, include
import notifications.urls

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('clients', views.index, name='clients'),
    path('tasks/inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('tasks', views.tasks, name='tasks'),
]
