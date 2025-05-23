"""chronocast URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from main import views as main_views

# Non-localized URLs (like API endpoints)
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include('main.api_urls')), # Comment out or remove this line
    path('i18n/', include('django.conf.urls.i18n')),
]

# Add localized URLs
urlpatterns += i18n_patterns(
    path('', main_views.index, name='index'),
    path('search', main_views.search_words, name='search_words'),
    path('', include('main.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
