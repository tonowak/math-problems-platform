from django.views.generic import View
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import Tag
from users.permissions import StaffOnly

tag_types = [
    "Geometria",
    "Algebra i Teoria Liczb",
    "Kombinatoryka",
    "Analiza",
    "Inne",
    "Źródło",
    "Trudność",
    "Grupa",
]

class IndexView(StaffOnly, View):
    def get(self, request):
        tag_data = [[] for i in range(len(tag_types))]
        for tag in Tag.objects.filter(attachable=True):
            tag_data[tag.type_id].append(tag)
        tag_data = list(zip(tag_types, tag_data))

        return render(request, 'tags/index.html', {'tag_data': tag_data});

class AddView(StaffOnly, View):
    def get(self, request):
        return render(request, 'tags/add.html', {'tag_types': tag_types})

    def post(self, request):
        tag = Tag(name=request.POST['name'], type_id=request.POST['category'])
        tag.save()
        messages.success(request, "Dodano tag!")
        return redirect('tags:add')


class EditView(StaffOnly, View):
    def post(self, request, pk):
        tag = get_object_or_404(Tag, pk=pk)
        tag.name = request.POST['name']
        tag.save()
        messages.success(request, "Zapisano zmiany!")
        return redirect('tags:index')
