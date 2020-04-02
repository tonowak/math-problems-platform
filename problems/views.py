from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import Problem
from tags.models import Tag

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

        tag_data = []
        for tag in Tag.objects.all():
            tag_data.append((tag, bool(problem.tag_set.filter(pk=tag.pk))))

        return render(request, 'problems/edit.html', {
            'problem': problem,
            'tag_data': tag_data,
        })

    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.content=request.POST['statement']
        tags = request.POST.getlist('tags[]')
        problem.tag_set.clear()
        for tag_id in tags:
            problem.tag_set.add(Tag.objects.get(pk=tag_id))
        problem.save()
        messages.success(request, "Zapisano zmiany!")
        return HttpResponseRedirect(reverse('problems:edit', args=[pk]))

class DeleteView(generic.View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.delete();
        messages.success(request, "Zadanie usunięte!")
        return HttpResponseRedirect(reverse('problems:index'))
