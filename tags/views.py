from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import Tag

tag_types = [
    "Geometria",
    "ATL",
    "Kombinatoryka",
    "Analiza",
    "Inne",
    "Źródło",
    "Trudność",
]

class IndexView(generic.View):
    def get(self, request):
        tag_data = [[] for i in range(len(tag_types))]
        for tag in Tag.objects.all():
            tag_data[tag.type_id].append(tag)

        tag_data = list(zip(tag_types, tag_data))
        return render(request, 'tags/index.html', {'tag_data': tag_data})

class AddView(generic.View):
    def get(self, request):
        return render(request, 'tags/add.html', {'tag_types': tag_types})

    def post(self, request):
        tag = Tag(name=request.POST['name'], type_id=request.POST['category'])
        tag.save()
        messages.success(request, "Dodano tag!")
        return HttpResponseRedirect(reverse('tags:add'))
