from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render

from .models import Problem

class IndexView(generic.ListView):
    template_name = 'problems/index.html'
    context_object_name = 'problemset'

    def get_queryset(self):
        return Problem.objects.all()

class AddView(generic.View):
    def get(self, request):
        return render(request, 'problems/add.html')

    def post(self, request):
        problem = Problem(content=request.POST['statement'])
        problem.save()
        return HttpResponseRedirect(reverse('problems:add'))

