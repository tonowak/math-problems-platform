from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator

from .models import Problem
from tags.models import Tag
from users.permissions import staff_only, url_404, has_access_to_problem

@method_decorator(staff_only, name='dispatch')
class IndexView(generic.View):
    def get(self, request):
        problems_data = []
        for problem in Problem.objects.all():
            problems_data.append((problem, problem.tag_set.all()))
        return render(request, 'problems/index.html', {'problems_data': problems_data})

@method_decorator(staff_only, name='dispatch')
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
        if not has_access_to_problem(request.user, problem):
            return redirect(url_404)
        return render(request, 'problems/details.html', {
            'problem': problem,
            'tags': problem.tag_set.order_by('type_id', 'id'),
        })

@method_decorator(staff_only, name='dispatch')
class EditView(generic.View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        tag_data = []
        for tag in Tag.objects.order_by('type_id', 'id'):
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

@method_decorator(staff_only, name='dispatch')
class DeleteView(generic.View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.delete();
        messages.success(request, "Zadanie usunięte!")
        return HttpResponseRedirect(reverse('problems:index'))
