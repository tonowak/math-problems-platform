from django.shortcuts import render
from django.views.generic import View
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User

from .permissions import StaffOnly, UserpageAccess
from tags.models import Tag

def login_view(request):
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('users:login')

class IndexView(StaffOnly, View):
    def get(self, request):
        users = User.objects.all()
        return render(request, 'users/index.html', {
            'users': User.objects.all(),
        })

def back_from_problem(request):
    return render(request, 'users/back_from_problem.html')

class EditUser(UserpageAccess, View):
    def get(self, request, u_id):
        user = get_object_or_404(User, id=u_id)
        all_tags = Tag.objects.filter(type_id=7).order_by('type_id', 'id')
        selected_tags = []
        for tag in all_tags:
            if user.tag_set.filter(pk=tag.pk):
                selected_tags.append(tag)
        context = {
            'editing_user': user,
            'all_tags': all_tags,
            'selected_tags': selected_tags,
        }
        return render(request, 'users/edit.html', context)
    
    def post(self, request, u_id):
        user = get_object_or_404(User, id=u_id)
        user.first_name = request.POST['first_name']
        user.last_name  = request.POST['last_name']
        if request.user.is_staff:
            tags = request.POST.getlist('tags[]') if 'tags[]' in request.POST else []
            user.tag_set.clear()
            for tag_id in tags:
                user.tag_set.add(Tag.objects.get(id=tag_id))
        user.save()
        return redirect('users:edit', u_id)

