from django.contrib import admin
from django.urls import path
from views import login_interface
urlpatterns = [
    path('', login_interface),#登陆主路由

]
