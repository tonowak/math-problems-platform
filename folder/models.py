from django.db import models
from django.contrib.auth.models import User
from django.http import Http404

from problems.models import Problem
from tags.models import Tag

class Folder(models.Model):
    parent         = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    folder_name    = models.CharField(max_length=100)
    pretty_name    = models.CharField(max_length=100)
    tag_set        = models.ManyToManyField(Tag)
    problem_set    = models.ManyToManyField(Problem, through='ProblemPlace')
    created_by     = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    show_stats     = models.IntegerField(default=1)
    show_solution  = models.IntegerField(default=1)

    def __str__(self):
        return self.pretty_name

class ProblemPlace(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    place = models.IntegerField()

import unicodedata, re
def convert_pretty_to_folder_name(pretty):
    pretty = unicodedata.normalize('NFD', pretty)
    pretty = u"".join([c for c in pretty if not unicodedata.combining(c)])
    pretty = pretty.replace('ł', 'l')
    pretty = pretty.replace('Ł', 'L')
    folder = ''
    for c in pretty:
        if c.isalnum():
            folder += c
        else:
            folder += '-'
    return re.sub('-+', '-', folder)

# remove '/' and '/' around folder_path
def fix_path(folder_path):
    if folder_path[0] == '/':
        folder_path = folder_path[1:]
    if folder_path and folder_path[-1] == '/':
        folder_path = folder_path[:-1]
    return folder_path

def get_folder(folder_path):
    folder_path = fix_path(folder_path)
    root_list = Folder.objects.filter(parent=None)
    assert len(root_list) == 1
    root = root_list[0]
    if folder_path == 'all':
        return root

    folder_path = folder_path.split('/')
    folder = root
    for s in folder_path:
        folder = Folder.objects.filter(parent=folder, folder_name=s)
        if len(folder) == 0:
            raise Http404("Nie istnieje taka ścieżka")
        assert len(folder) == 1
        folder = folder[0]
    return folder

def get_parent_path(path):
    if path != 'all' and '/' in path:
        return path[0:path.rindex('/')]
    else:
        return 'all'

def get_son_path(parent, folder_name):
    if parent == 'all':
        return folder_name
    return parent + '/' + folder_name

def get_parent_paths(path):
    ret_list = []
    path = path.split('/')
    prefix = ''
    for s in path:
        if prefix != '':
            prefix += '/'
        prefix += s
        f = get_folder(prefix)
        ret_list.append((prefix, f.pretty_name))
    return ret_list

def add_folder(parent, pretty_name, created_by=None):
    folder_name = convert_pretty_to_folder_name(pretty_name)
    assert Folder.objects.filter(parent=parent, folder_name=folder_name).count() == 0
    son = Folder(
        parent=parent, 
        folder_name=folder_name, 
        pretty_name=pretty_name, 
        created_by=created_by,
        show_solution=parent.show_solution,
        show_stats=parent.show_stats,
    )
    son.save()
    return son

def rename_folder(folder, pretty_name):
    assert folder.parent != None
    assert Folder.objects.filter(parent=parent, folder_name=folder_name).count() == 0
    folder.pretty_name = pretty_name
    folder.folder_name = convert_pretty_to_folder_name(pretty_name)
    folder.save()

