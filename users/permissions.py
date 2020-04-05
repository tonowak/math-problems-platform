from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

url_404 = 'users:login'

staff_only = user_passes_test(lambda u: u.is_staff, login_url=url_404)

from folder.models import Folder

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
    if user.is_staff:
        return True
    if not user.is_authenticated:
        return False
    f = folder
    while f.parent:
        if has_direct_access_to_folder(user, f):
            return True
        f = Folder.objects.get(id=f.parent.id)
    if has_access_in_subtree(user, folder):
        return True
    return False

def has_access_to_problem(user, problem):
    if user.is_staff:
        return True
    for folder in problem.folder_set.all():
        if has_access_to_folder(user, folder):
            return True
    return False
