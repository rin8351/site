from django.urls import path
from . import views

app_name = 'main'

# All URL patterns
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search_words, name='search_words'),  # now this maps to '/api/search'
    path('flights/<str:flight_html_file>', views.serve_flight_html, name='serve_flight_html'),
]
