from django.test import TestCase
import os

from .models import Folder
from tiled_math.settings import BASE_DIR
from folder.models import Folder
from folder.views import convert_pretty_to_folder_name

def add_sample_folders():
    path = os.path.join(BASE_DIR, 'folder/files/sample_folders.txt')
    folder_stack = [Folder.objects.get(parent=None)]
    with open(path) as input_file:
        added_folders = 0
        for line in input_file:
            line = line.replace('\n', '')
            name = line.lstrip(' ')
            if name == '':
                continue

            leading_spaces = len(line) - len(name)
            while leading_spaces != len(folder_stack) - 1:
                folder_stack.pop()

            formatted_name = convert_pretty_to_folder_name(name)
            folder = Folder(parent=folder_stack[-1], pretty_name=name, folder_name=formatted_name, created_by=None)
            folder.save()
            folder_stack.append(folder)
            added_folders += 1
