from django.urls import path
from . import views

app_name = 'main'

# Non-localized URLs
urlpatterns = [
    path('api/search', views.search_words, name='search_words'),
]

# Localized URLs - these will be included in i18n_patterns
localized_urlpatterns = [
    path('', views.index, name='index'),
]
