import os
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import get_language

def index(request):
    current_language = get_language()
    base_dir = os.path.join(settings.BASE_DIR, 'main')
    file_path = os.path.join(base_dir, f'description_{current_language}.txt')
    file_path2 = os.path.join(base_dir, f'links_{current_language}.txt')
    file_path3 = os.path.join(base_dir, f'ds_{current_language}.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        description = file.read()

    with open(file_path2, 'r', encoding='utf-8') as file2:
        links = file2.read()
    
    with open(file_path3, 'r', encoding='utf-8') as file3:
        ds = file3.read()
    
    context = {'description': description, 'links': links, 'ds': ds}
    return render(request, 'main/index.html', context)
