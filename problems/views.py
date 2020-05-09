from django.http import HttpResponseRedirect
from django.views.generic import View
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import Problem, has_solved_task, get_solutionscore, convert_string_to_number_list, reformat_string_number_list
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
        context = {
            'all_tags': problem_tags(),
            'selected_tags': selected_tags,
        }
        problems = problems.order_by('-id')
        show_all = 'show_all' in request.GET
        context['show_all'] = show_all

        problems_data = []
        for problem in problems:
            problems_data.append((problem, problem.tag_set.order_by('type_id', 'id').filter(attachable=True)))
        context['found_cnt'] = len(problems_data)
        upper_bound = 200
        if not show_all and len(problems_data) > upper_bound:
            problems_data = problems_data[:upper_bound]
        context['showed_cnt'] = len(problems_data)
        context['problems_data'] = problems_data

        return render(request, 'problems/index.html', context)

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
        if 'answer_checker_enabled' in request.POST:
            problem.answer_checker = reformat_string_number_list(request.POST['answer_checker_list_string'])
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

        can_see_sol = has_access_to_solution(request.user, problem)
        context = {
            'problem': problem,
            'statement': problem.statement,
            'solved_task': has_solved_task(problem, request.user),
            'can_see_solution': can_see_sol,
        }
        if can_see_sol and inside_get('show_hints'):
            context['hints'] = problem.hints
        if can_see_sol and inside_get('show_answer'):
            context['answer'] = problem.answer
            context['answer_checker'] = convert_string_to_number_list(problem.answer_checker)
        if can_see_sol and inside_get('show_solution'):
            context['solution'] = problem.solution
        if request.user.is_staff:
            context['tags'] = problem.tag_set.order_by('type_id', 'id').filter(attachable=True)
        if has_access_to_stats(request.user, problem):
            context['solved_cnt'] = 'TODO'

        return render(request, 'problems/details.html', context)

class ClaimView(ProblemAccess, View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)

        if problem.has_answer_checker():
            return redirect('problems:submissions', pk)

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
            'answer_checker': convert_string_to_number_list(problem.answer_checker),
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
        if 'answer_checker_enabled' in request.POST:
            problem.answer_checker = reformat_string_number_list(request.POST['answer_checker_list_string'])
        else:
            problem.answer_checker = ''
        problem.save()
        messages.success(request, "Zapisano zmiany!")
        return redirect('problems:edit', pk)

class DeleteView(StaffOnly, View):
    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk=pk)
        problem.delete();
        messages.success(request, "Zadanie usunięte!")
        return redirect('problems:index')
