from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import Problem, SolutionTag, SourceTag

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
        messages.success(request, "Dodano zadanie!")
        return HttpResponseRedirect(reverse('problems:add'))

class DetailsView(generic.View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        return render(request, 'problems/details.html', {'problem': problem})

class EditView(generic.View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        return render(request, 'problems/edit.html', {'problem': problem})

class TagsView(generic.View):
    def get(self, request):
       solution_tags = SolutionTag.objects.all()
       source_tags = SourceTag.objects.all()
       return render(request, 'problems/tags.html', {
           'solution_tags': solution_tags,
           'source_tags': source_tags,
        })

class AddSolutionTagView(generic.View):
    def get(self, request):
        return render(request, 'problems/add_solution_tag.html')

    def post(self, request):
        solution_tag = SolutionTag(name=request.POST['name'])
        solution_tag.save()
        messages.success(request, "Dodano tag!")
        return HttpResponseRedirect(reverse('problems:add_solution_tag'))

class AddSourceTagView(generic.View):
    def get(self, request):
        return render(request, 'problems/add_source_tag.html')

    def post(self, request):
        source_tag = SourceTag(name=request.POST['name'])
        source_tag.save()
        messages.success(request, "Dodano tag!")
        return HttpResponseRedirect(reverse('problems:add_source_tag'))

