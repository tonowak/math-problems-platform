from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator

from .models import Problem
from tags.models import Tag
from users.permissions import staff_only, url_403, has_access_to_problem

def problem_tags():
    return Tag.objects.exclude(type_id=7).order_by('type_id', 'id')

def attachable_tags():
    return problem_tags().filter(attachable=True)

def process_tags(problem, tag_list):
    problem.tag_set.clear()
    for tag_id in tag_list:
        problem.tag_set.add(Tag.objects.get(pk=tag_id))
    for i in range(4):
        if problem.tag_set.filter(type_id=i):
            problem.tag_set.add(Tag.objects.get(type_id=i, attachable=False))
    return problem

@method_decorator(staff_only, name='dispatch')
class IndexView(generic.View):
    def get(self, request):
        tag_filter = request.GET.getlist('tags[]', [])
        problems = Problem.objects.all()
        for tag_id in tag_filter:
            problems = problems.filter(tag__id=tag_id)

        problems_data = []
        for problem in problems:
            problems_data.append((problem, problem.tag_set.order_by('type_id', 'id').filter(attachable=True)))

        tag_data = []
        for tag in problem_tags():
            tag_data.append((tag, str(tag.id) in tag_filter))

        return render(request, 'problems/index.html', {
            'problems_data': problems_data,
            'tag_data': tag_data,
        })

@method_decorator(staff_only, name='dispatch')
class AddView(generic.View):
    def get(self, request):
        return render(request, 'problems/add.html', {'tag_data': attachable_tags()})

    def post(self, request):
        problem = Problem(
            statement = request.POST['statement'],
            hints = request.POST['hints'],
            answer = request.POST['answer'],
            solution = request.POST['solution'],
            created_by = request.user,
        )
        problem.save()
        process_tags(problem, request.POST.getlist('tags[]')).save()
        messages.success(request, "Dodano zadanie!")
        return HttpResponseRedirect(reverse('problems:add'))

class DetailsView(generic.View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        if not has_access_to_problem(request.user, problem):
            return redirect(url_403)

        def inside_get(s):
            ret = request.user.is_staff or s in request.GET
            return ret

        return render(request, 'problems/details.html', {
            'problem': problem,
            'tags': problem.tag_set.order_by('type_id', 'id').filter(attachable=True),
            'show_hints': inside_get('show_hints') or inside_get('show_solution'),
            'show_answer': inside_get('show_answer') or inside_get('show_solution'),
            'show_solution': inside_get('show_solution'),
            'solved_task': request.user.problem_set.filter(id=problem.id).exists(),
        })

class ClaimView(generic.View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        if not has_access_to_problem(request.user, problem):
            return redirect(url_403)

        if request.user.problem_set.filter(id=problem.id).exists():
            request.user.problem_set.remove(problem)
        else:
            request.user.problem_set.add(problem)

        print(request.POST)
        if 'stay' in request.POST:
            return redirect('users:back_from_problem')
        else:
            return redirect('problems:details', pk)

@method_decorator(staff_only, name='dispatch')
class EditView(generic.View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        tag_data = []
        for tag in attachable_tags():
            tag_data.append((tag, bool(problem.tag_set.filter(pk=tag.pk))))
        return render(request, 'problems/edit.html', {
            'problem': problem,
            'tag_data': tag_data,
        })

    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.statement = request.POST['statement']
        problem.hints = request.POST['hints']
        problem.answer = request.POST['answer']
        problem.solution = request.POST['solution']
        tags = request.POST.getlist('tags[]')
        problem = process_tags(problem, request.POST.getlist('tags[]'))
        problem.save()
        messages.success(request, "Zapisano zmiany!")
        return HttpResponseRedirect(reverse('problems:edit', args=[pk]))

@method_decorator(staff_only, name='dispatch')
class DeleteView(generic.View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.delete();
        messages.success(request, "Zadanie usunięte!")
        return redirect('problems:index')
