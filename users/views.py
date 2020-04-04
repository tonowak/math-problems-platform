from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User

from .permissions import staff_only
from tags.models import Tag

def login_view(request):
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('users:login')

@staff_only
def index_view(request):
    users = User.objects.all()
    return render(request, 'users/index.html', {
        'users': User.objects.all(),
    })

class EditUser(generic.View):
    def has_permission(self, request, u_id):
        if request.user.is_staff or request.user.id == u_id:
            return True
        return False

    def get(self, request, u_id):
        if not self.has_permission(request, u_id):
            return redirect('users:login')
        user = get_object_or_404(User, id=u_id)
        context = {
            'user': user
        }
        if request.user.is_staff:
            tag_data = []
            for tag in Tag.objects.filter(type_id=7).order_by('type_id', 'id'):
                tag_data.append((tag, bool(user.tag_set.filter(pk=tag.pk))))
            context['tag_data'] = tag_data
        return render(request, 'users/edit.html', context)
    
    def post(self, request, u_id):
        if not self.has_permission(request, u_id):
            return redirect('users:login')
        user = get_object_or_404(User, id=u_id)
        user.first_name = request.POST['first_name']
        user.last_name  = request.POST['last_name']
        if request.user.is_staff and 'tags[]' in request.POST:
            tags = request.POST.getlist('tags[]')
            user.tag_set.clear()
            for tag_id in tags:
                user.tag_set.add(Tag.objects.get(id=tag_id))
        user.save()
        return redirect('users:edit', u_id)

