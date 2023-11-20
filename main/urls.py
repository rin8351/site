from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Пример URL-пути к домашней странице
]
