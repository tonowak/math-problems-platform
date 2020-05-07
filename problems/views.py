from django.http import HttpResponseRedirect
from django.views.generic import View
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import Problem, has_solved_task, get_solutionscore
from tags.models import Tag
from users.permissions import StaffOnly, ProblemAccess
from users.permissions import has_access_to_solution, has_access_to_stats

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

class IndexView(StaffOnly, View):
    def get(self, request):
        tag_filter = request.GET.getlist('tags[]', [])
        problems = Problem.objects.all()
        selected_tags = []
        for tag_id in tag_filter:
            problems = problems.filter(tag__id=tag_id)
            selected_tags.append(Problem.objects.get(id=tag_id))
        problems = problems.order_by('-id')

        problems_data = []
        for problem in problems:
            problems_data.append((problem, problem.tag_set.order_by('type_id', 'id').filter(attachable=True)))

        return render(request, 'problems/index.html', {
            'problems_data': problems_data,
            'all_tags': problem_tags(),
            'selected_tags': selected_tags,
        })

class AddView(StaffOnly, View):
    def get(self, request):
        return render(request, 'problems/add.html', {'all_tags': attachable_tags()})

    def post(self, request):
        problem = Problem(
            statement = request.POST['statement'],
            hints = request.POST['hints'],
            answer = request.POST['answer'],
            solution = request.POST['solution'],
            staff_comment = request.POST['staff_comment'],
            solution_comment = request.POST['solution_comment'],
            created_by = request.user,
        )
        problem.save()
        process_tags(problem, request.POST.getlist('tags[]')).save()
        messages.success(request, "Dodano zadanie!")
        return HttpResponseRedirect(reverse('problems:add'))

class DetailsView(ProblemAccess, View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)

        def inside_get(s):
            ret = request.user.is_staff or s in request.GET
            return ret

        return render(request, 'problems/details.html', {
            'problem': problem,
            'tags': problem.tag_set.order_by('type_id', 'id').filter(attachable=True),
            'show_hints': inside_get('show_hints') or inside_get('show_solution'),
            'show_answer': inside_get('show_answer') or inside_get('show_solution'),
            'show_solution': inside_get('show_solution'),
            'access_to_solution': has_access_to_solution(request.user, problem),
            'access_to_stats': has_access_to_stats(request.user, problem),
            'solved_task': has_solved_task(problem, request.user),
            'solved_cnt': 'TODO',
        })

class ClaimView(ProblemAccess, View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)

        ss = get_solutionscore(problem=problem, user=request.user)
        ss.claiming = not ss.claiming
        ss.save()

        if 'stay' in request.POST:
            return redirect('users:back_from_problem')
        else:
            return redirect('problems:details', pk)

class EditView(StaffOnly, View):
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        selected_tags = []
        for tag in attachable_tags():
            if problem.tag_set.filter(pk=tag.pk):
                selected_tags.append(tag)

        return render(request, 'problems/edit.html', {
            'problem': problem,
            'all_tags': attachable_tags(),
            'selected_tags': selected_tags,
        })

    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.statement = request.POST['statement']
        problem.hints = request.POST['hints']
        problem.answer = request.POST['answer']
        problem.solution = request.POST['solution']
        problem.staff_comment = request.POST['staff_comment']
        problem.solution_comment = request.POST['solution_comment']
        tags = request.POST.getlist('tags[]')
        problem = process_tags(problem, request.POST.getlist('tags[]'))
        problem.save()
        messages.success(request, "Zapisano zmiany!")
        return HttpResponseRedirect(reverse('problems:edit', args=[pk]))

class DeleteView(StaffOnly, View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.delete();
        messages.success(request, "Zadanie usunięte!")
        return redirect('problems:index')
