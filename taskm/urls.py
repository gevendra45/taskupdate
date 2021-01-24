"""taskm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from taskupdate.views import (register, login, logout, fetch_users, create_project, view_project, 
		update_project, delete_project, create_task, view_task, update_task, delete_task, 
		create_subtask, view_subtask, update_subtask, delete_subtask)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('fetchusers/', fetch_users),
    path('createproject/', create_project),
    path('viewproject/', view_project),
    path('updateproject/', update_project),
    path('deleteproject/', delete_project),
    path('createtask/', create_task),
    path('viewtask/', view_task),
    path('updatetask/', update_task),
    path('deletetask/', delete_task),
    path('createsubtask/', create_subtask),
    path('viewsubtask/', view_subtask),
    path('updatesubtask/', update_subtask),
    path('deletesubtask/', delete_subtask),
]