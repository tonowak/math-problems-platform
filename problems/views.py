from django.shortcuts import render
from django.views import generic

from .models import Problem

class IndexView(generic.ListView):
    template_name = 'problems/index.html'
    context_object_name = 'problemset'

    def get_queryset(self):
        return Problem.objects.all()

class AddView(generic.View):
    def get(self, request):
        return render(request, 'problems/add.html')

