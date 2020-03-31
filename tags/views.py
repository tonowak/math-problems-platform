from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import Tag

class IndexView(generic.ListView):
    template_name = 'tags/index.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.all()

class AddView(generic.View):
    def get(self, request):
        return render(request, 'tags/add.html')

    def post(self, request):
        tag = Tag(name=request.POST['name'])
        tag.save()
        messages.success(request, "Dodano tag!")
        return HttpResponseRedirect(reverse('tags:add'))
