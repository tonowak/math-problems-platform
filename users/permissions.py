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

def wrapper(user_test):
    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if user_test(request, **kwargs):
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrap
    return decorator

class UserpageAccess(UserAccessMixin):
    def has_permission(self, user, **kwargs):
        return user.is_staff or user.id == kwargs['u_id']

def has_direct_access_to_folder(user, folder):
    if folder.parent == None:
        return True
    for tag in user.tag_set.all():
        if folder.tag_set.filter(id=tag.id):
            return True;
    return False

def has_access_in_subtree(user, folder):
    if has_direct_access_to_folder(user, folder):
        return True
    for son in Folder.objects.filter(parent=folder.id).all():
        if has_direct_access_to_folder(user, son):
            return True
    return False

def has_access_to_folder(user, folder):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    f = folder
    while f.parent:
        if has_direct_access_to_folder(user, f):
            return True
        f = Folder.objects.get(id=f.parent.id)
    if has_access_in_subtree(user, folder):
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

