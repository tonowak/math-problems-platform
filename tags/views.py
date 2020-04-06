from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator

from .models import Tag
from users.permissions import staff_only

tag_types = [
    "Geometria",
    "ATL",
    "Kombinatoryka",
    "Analiza",
    "Inne",
    "Źródło",
    "Trudność",
    "Grupa",
]

@method_decorator(staff_only, name='dispatch')
class IndexView(generic.View):
    def get(self, request):
        tag_data = [[] for i in range(len(tag_types))]
        for tag in Tag.objects.all():
            tag_data[tag.type_id].append(tag)
        tag_data = list(zip(tag_types, tag_data))

        return render(request, 'tags/index.html', {'tag_data': tag_data});

@method_decorator(staff_only, name='dispatch')
class AddView(generic.View):
    def get(self, request):
        return render(request, 'tags/add.html', {'tag_types': tag_types})

    def post(self, request):
        tag = Tag(name=request.POST['name'], type_id=request.POST['category'])
        tag.save()
        messages.success(request, "Dodano tag!")
        return HttpResponseRedirect(reverse('tags:add'))


@method_decorator(staff_only, name='dispatch')
class EditView(generic.View):
    def post(self, request, pk):
        tag = get_object_or_404(Tag, pk=pk)
        tag.name = request.POST['name']
        tag.save()
        messages.success(request, "Zapisano zmiany!")
        return HttpResponseRedirect(reverse('tags:index'))
