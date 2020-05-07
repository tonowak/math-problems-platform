from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from functools import wraps

from folder.models import get_folder, Folder
from problems.models import Problem

class UserAccessMixin(object):
    def has_permission(self, user, **kwargs):
        return True

    def dispatch(self, request, *args, **kwargs):
        if self.has_permission(request.user, **kwargs):
            return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)
        else:
            if not request.user.is_authenticated:
                return redirect('users:login')
            else:
                raise PermissionDenied

class StaffOnly(UserAccessMixin):
    def has_permission(self, user, **kwargs):
        return user.is_staff

class UserpageAccess(UserAccessMixin):
    def has_permission(self, user, **kwargs):
        return user.is_staff or user.id == kwargs['u_id']

def recalculate_indirect_folder_tags():
    for folder in Folder.objects.all():
        folder.indirect_tag_set.clear()

    def add_to_subtree(folder, tag):
        folder.indirect_tag_set.add(tag)
        for son in Folder.objects.filter(parent=folder).all():
            add_to_subtree(son, tag)

    def add_to_ancestors(folder, tag):
        folder.indirect_tag_set.add(tag)
        if folder.parent != None:
            add_to_ancestors(folder.parent, tag)

    for folder in Folder.objects.all():
        for tag in folder.direct_tag_set.all():
            add_to_subtree(folder, tag)
            add_to_ancestors(folder, tag)

def has_access_to_folder(user, folder):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    for tag in user.tag_set.all():
        if folder.indirect_tag_set.filter(id=tag.id).exists():
            return True
    return False

class FolderAccess(UserAccessMixin):
    def has_permission(self, user, **kwargs):
        f = get_folder(kwargs['folder_path'])
        return has_access_to_folder(user, f)

def has_access_to_problem(user, problem):
    if user.is_staff:
        return True
    for folder in problem.folder_set.all():
        if has_access_to_folder(user, folder):
            return True
    return False

class ProblemAccess(UserAccessMixin):
    def has_permission(self, user, **kwargs):
        p = get_object_or_404(Problem, pk=kwargs['pk'])
        return has_access_to_problem(user, p)

def has_access_to_solution(user, problem):
    if user.is_staff:
        return True
    ret = False
    for folder in problem.folder_set.all():
        if has_access_to_folder(user, folder):
            if not folder.show_solution:
                return False
            ret = True
    return ret

def has_access_to_stats(user, problem):
    if user.is_staff:
        return True
    ret = False
    for folder in problem.folder_set.all():
        if has_access_to_folder(user, folder):
            if not folder.show_stats:
                return False
            ret = True
    return ret

