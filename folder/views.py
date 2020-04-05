from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.utils.decorators import method_decorator

from .models import Folder
from problems.models import Problem
from tags.models import Tag
from tags.views import tag_types
from users.permissions import has_access_to_folder, url_404, staff_only

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

def get_context(path):
    path = fix_path(path)
    folder = get_folder(path)
    tag_data = []
    group_type = tag_types.index("Grupa")
    for tag in Tag.objects.filter(type_id=group_type).order_by('type_id', 'id'):
        tag_data.append((tag, folder.tag_set.filter(pk=tag.pk).exists()))

    return {
        'folder_path': path,
        'folder': folder,
        'sons': Folder.objects.filter(parent=folder),
        'son_path_prefix': path + '/' if path != 'all' else '',
        'parent_path': get_parent_path(path),
        'parent_paths': get_parent_paths(path),
        'problems': folder.problem_set.all(),
        'tag_data': tag_data,
    }

class IndexView(generic.View):
    def get(self, request, folder_path):
        if not has_access_to_folder(request.user, get_folder(folder_path)):
            return redirect(url_404)
        context = get_context(folder_path)
        if not request.user.is_staff:
            context['sons'] = []
            for son in Folder.objects.filter(parent=context['folder']).all():
                if has_access_to_folder(request.user, son):
                    context['sons'].append(son)
        context['problems'] = []
        for problem in context['folder'].problem_set.all():
            context['problems'].append(
                    (problem, problem.claiming_user_set.filter(id=request.user.id).exists()))
        return render(request, 'folder/index.html', context)

@method_decorator(staff_only, name='dispatch')
class EditView(generic.View):
    def get(self, request, folder_path):
        return render(request, 'folder/edit.html', get_context(folder_path))

@method_decorator(staff_only, name='dispatch')
class AddFolder(generic.View):
    def post(self, request, folder_path):
        folder = get_folder(folder_path)
        pretty_name = request.POST['pretty_name']
        folder_name = convert_pretty_to_folder_name(pretty_name)
        if folder_name == '' or folder_name == '-':
            messages.error(request, 'Nazwa folderu jest pusta.')
            return redirect('folder:edit', folder_path)

        if not Folder.objects.filter(parent=folder, folder_name=folder_name):
            son = Folder(parent=folder, pretty_name=pretty_name, folder_name=folder_name)
            son.save()
            messages.success(request, 'Dodano folder!')
        else:
            messages.error(request, 'Taki folder już istnieje.')
        return redirect('folder:edit', folder_path)

@method_decorator(staff_only, name='dispatch')
class EditFolderName(generic.View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        pretty_name = request.POST['pretty_name']
        folder_name = convert_pretty_to_folder_name(pretty_name)
        if folder_name == '' or folder_name == '-':
            return redirect('folder:edit', folder_path)
        if folder_path == 'all':
            messages.error(request, 'Nie można zmienić nazwę głównego folderu.')
            return redirect('folder:edit', folder_path)
        parent_f = get_folder(get_parent_path(folder_path))
        if Folder.objects.filter(parent=parent_f, folder_name=folder_name):
            messages.error(request, 'Taki folder już istnieje.')
            return redirect('folder:edit', folder_path)

        f.folder_name = folder_name
        f.pretty_name = pretty_name
        f.save()
        messages.success(request, 'Zmieniono nazwę!')
        new_path = get_son_path(get_parent_path(folder_path), folder_name)
        return redirect('folder:edit', new_path)

@method_decorator(staff_only, name='dispatch')
class DeleteFolder(generic.View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        pretty_name = request.POST['pretty_name']
        matches = Folder.objects.filter(parent=f, pretty_name=pretty_name)
        if len(matches) != 1:
            messages.error(request, 'Nastąpił błąd krytyczny.')
            return redirect('folder:edit', folder_path)
        son = matches[0]

        son.delete()
        messages.success(request, 'Usunięto!')
        return redirect('folder:edit', folder_path)

@method_decorator(staff_only, name='dispatch')
class AddProblem(generic.View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        p_id = request.POST['p_id']
        if p_id == '':
            return redirect('folder:edit', folder_path)

        problem = get_object_or_404(Problem, pk=p_id)
        f.problem_set.add(problem)
        messages.success(request, 'Dodano zadanie!')
        return redirect('folder:edit', folder_path)

@method_decorator(staff_only, name='dispatch')
class DeleteProblem(generic.View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        p_id = request.POST['p_id']
        problem = get_object_or_404(Problem, pk=p_id)
        f.problem_set.remove(problem)
        messages.success(request, 'Usunięto zadanie!')
        return redirect('folder:edit', folder_path)

@method_decorator(staff_only, name='dispatch')
class EditTags(generic.View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        tags = request.POST.getlist('tags[]')
        f.tag_set.clear()
        for tag_id in tags:
            f.tag_set.add(Tag.objects.get(id=tag_id))
        f.save()
        messages.success(request, 'Zmieniono tagi!')
        return redirect('folder:edit', folder_path)
