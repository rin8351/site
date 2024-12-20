from django.urls import path
from . import views

app_name = 'main'

# All URL patterns
urlpatterns = [
    path('', views.index, name='index'),
    path('api/search', views.search_words, name='search_words'),
]
