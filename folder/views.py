from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.shortcuts import render

from .models import Folder

def get_folder(folder_path):
    root_list = Folder.objects.filter(parent_folder=None)
    assert len(root_list) == 1
    root = root_list[0]

    if len(folder_path) and folder_path[-1] == '/':
        folder_path = folder_path[:-1]
    folder_path = folder_path.split('/')
    print(folder_path)

class IndexView(generic.View):
    def get(self, request, folder_path = '/'):
        print("index view")
        folder = get_folder(folder_path)
        return render(request, 'folder/index.html')

class AddView(generic.View):
    def get(self, request, folder_path = '/'):
        print("add view")
        folder = get_folder(folder_path)
        return render(request, 'folder/index.html')

