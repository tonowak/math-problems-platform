from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect

from .models import Folder

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

def get_context(path):
    path = fix_path(path)
    folder = get_folder(path)
    parent_path = ''
    if path != 'all' and '/' in path:
        parent_path = path[0:path.rindex('/')]
    elif path != 'all':
        parent_path = 'all'

    return {
        'folder_path': path,
        'folder': folder,
        'sons': Folder.objects.filter(parent=folder),
        'son_path_prefix': path + '/' if path != 'all' else '',
        # 'parent_path': parent_path,
        'parent_paths': get_parent_paths(path),
    }

class IndexView(generic.View):
    def get(self, request, folder_path):
        return render(request, 'folder/index.html', get_context(folder_path))

def redirect(func, folder_path):
    s = 'folder:' + func
    return HttpResponseRedirect(reverse(s, kwargs={'folder_path': folder_path}))

class AddView(generic.View):
    def get(self, request, folder_path):
        return render(request, 'folder/add.html', get_context(folder_path))

    def post(self, request, folder_path):
        context = get_context(folder_path)
        folder = context['folder']
        pretty_name = request.POST['pretty_name']
        folder_name = convert_pretty_to_folder_name(pretty_name)
        if folder_name == '' or folder_name == '-':
            return redirect('add', folder_path)
        context['pretty_name'] = pretty_name
        context['folder_name'] = folder_name

        if not Folder.objects.filter(parent=folder, folder_name=folder_name):
            son = Folder(parent=folder, pretty_name=pretty_name, folder_name=folder_name)
            son.save()
        return redirect('add', folder_path)

