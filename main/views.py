import os
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import get_language

def index(request):
    current_language = get_language()
    base_dir = os.path.join(settings.BASE_DIR, 'main')
    file_path = os.path.join(base_dir, f'description_{current_language}.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        description = file.read()
    
    return render(request, 'main/index.html', {'description': description})
