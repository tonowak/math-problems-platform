from django.shortcuts import render, redirect
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Folder, ProblemPlace
from .models import get_parent_path, get_parent_paths, convert_pretty_to_folder_name, fix_path
from .models import get_folder, add_folder, rename_folder
from problems.models import Problem, has_solved_task, SolutionScore
from tags.models import Tag
from tags.views import tag_types
from users.permissions import FolderAccess, StaffOnly
from users.permissions import has_access_to_folder, recalculate_indirect_folder_tags  

def get_context(path):
    path = fix_path(path)
    folder = get_folder(path)
    group_type = tag_types.index("Grupa")
    all_tags = folder.indirect_tag_set.all()
    selected_tags = []
    for tag in all_tags:
        if folder.direct_tag_set.filter(pk=tag.pk).exists():
            selected_tags.append(tag)
    problems = []
    for fp in ProblemPlace.objects.filter(folder=folder).order_by('place').all():
        problems.append(fp.problem)

    return {
        'folder_path': path,
        'folder': folder,
        'sons': Folder.objects.filter(parent=folder).order_by('pretty_name'),
        'son_path_prefix': path + '/' if path != 'all' else '',
        'parent_path': get_parent_path(path),
        'parent_paths': get_parent_paths(path),
        'problems': problems,
        'all_tags': all_tags,
        'selected_tags': selected_tags,
    }

class IndexView(FolderAccess, View):
    def get(self, request, folder_path):
        context = get_context(folder_path)
        if not request.user.is_staff:
            context['sons'] = []
            for son in Folder.objects.filter(parent=context['folder']).all():
                if has_access_to_folder(request.user, son):
                    context['sons'].append(son)
        context['problems'] = []
        for fp in ProblemPlace.objects.filter(folder=context['folder']).order_by('place').all():
            problem = fp.problem
            context['problems'].append(
                    (problem, has_solved_task(problem, request.user)))
        return render(request, 'folder/index.html', context)

class EditView(StaffOnly, View):
    def get(self, request, folder_path):
        return render(request, 'folder/edit.html', get_context(folder_path))

class AddFolder(StaffOnly, View):
    def post(self, request, folder_path):
        folder = get_folder(folder_path)
        pretty_name = request.POST['pretty_name']
        folder_name = convert_pretty_to_folder_name(pretty_name)
        if folder_name == '' or folder_name == '-':
            messages.error(request, 'Nazwa folderu jest pusta.')
            return redirect('folder:edit', folder_path)

        if not Folder.objects.filter(parent=folder, folder_name=folder_name):
            add_folder(folder, pretty_name, request.user)
            messages.success(request, 'Dodano folder!')
        else:
            messages.error(request, 'Taki folder już istnieje.')
        return redirect('folder:edit', folder_path)

class EditFolderName(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        pretty_name = request.POST['pretty_name']
        folder_name = convert_pretty_to_folder_name(pretty_name)
        if folder_name == '' or folder_name == '-':
            return redirect('folder:edit', folder_path)
        if folder_path == 'all':
            messages.error(request, 'Nie można zmienić nazwę głównego folderu.')
            return redirect('folder:edit', folder_path)
        parent_f = get_folder(get_parent_path(folder_path))
        if Folder.objects.filter(parent=parent_f, folder_name=folder_name):
            messages.error(request, 'Taki folder już istnieje.')
            return redirect('folder:edit', folder_path)

        rename_folder(f, pretty_name)
        messages.success(request, 'Zmieniono nazwę!')
        new_path = get_son_path(get_parent_path(folder_path), folder_name)
        return redirect('folder:edit', new_path)

class DeleteFolder(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        pretty_name = request.POST['pretty_name']
        matches = Folder.objects.filter(parent=f, pretty_name=pretty_name)
        if len(matches) != 1:
            messages.error(request, 'Nastąpił błąd krytyczny.')
            return redirect('folder:edit', folder_path)
        son = matches[0]

        son.delete()
        messages.success(request, 'Usunięto!')
        return redirect('folder:edit', folder_path)

class AddProblem(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        p_id = request.POST['p_id']
        if p_id == '':
            return redirect('folder:edit', folder_path)

        try:
            problem = Problem.objects.get(pk=p_id)
        except Problem.DoesNotExist:
            messages.error(request, 'To zadanie nie istnieje.')
            return redirect('folder:edit', folder_path)
        if f.problem_set.filter(id=problem.id).exists():
            messages.error(request, 'To zadanie jest już dodane.')
            return redirect('folder:edit', folder_path)

        cnt_p_inside_f = f.problem_set.count()
        ProblemPlace.objects.create(
            folder = f,
            problem = problem,
            place = cnt_p_inside_f
        )
        messages.success(request, 'Dodano zadanie!')
        return redirect('folder:edit', folder_path)

class DeleteProblem(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        p_id = request.POST['p_id']
        problem = get_object_or_404(Problem, pk=p_id)
        f.problem_set.remove(problem)
        messages.success(request, 'Usunięto zadanie!')
        return redirect('folder:edit', folder_path)

class EditTags(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        tags = request.POST.getlist('tags[]')
        tags = [Tag.objects.get(id=id) for id in tags]
        f.direct_tag_set.clear()
        for tag in tags:
            f.direct_tag_set.add(tag)
        recalculate_indirect_folder_tags()
        messages.success(request, 'Zmieniono tagi!')
        return redirect('folder:edit', folder_path)

class MoveProblemUp(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        p_id = request.POST['p_id']
        p_down = get_object_or_404(ProblemPlace, folder=f, problem=get_object_or_404(Problem, id=p_id))
        p_up   = get_object_or_404(ProblemPlace, folder=f, place=p_down.place - 1)
        p_down.place -= 1
        p_down.save()
        p_up.place += 1
        p_up.save()
        messages.success(request, 'Przesunięto zadanie!')
        return redirect('folder:edit', folder_path)

class Ranking(FolderAccess, View):
    # problem_list = list of (path, problems_in_this_folder) 
    def dfs(self, prefix, f, problem_list):
        if f.parent == None:
            prefix = '~'
        elif prefix:
            prefix += ' / ' + f.pretty_name
        else:
            prefix = f.pretty_name
        problems = []
        for fp in ProblemPlace.objects.filter(folder=f).order_by('place').all():
            problems.append(fp.problem)
        if len(problems) != 0:
            problem_list.append((prefix, problems))
        for son in Folder.objects.filter(parent=f).all():
            if has_access_to_folder(self.request.user, son):
                self.dfs(prefix, son, problem_list)

    def get(self, request, folder_path):
        # generate problem_list
        f = get_folder(folder_path)
        problem_list = []
        self.dfs('', f, problem_list)

        # take all users claiming at least one task from problem_list
        userlist = set()
        for prefix, problems in problem_list:
            for problem in problems:
                for solutionscore in SolutionScore.objects.filter(problem=problem).all():
                    user = solutionscore.user
                    if user not in userlist:
                        userlist.add(user)
                            
        # retrieve tags from request
        tags = []
        if 'tags[]' in request.GET:
            tags = [Tag.objects.get(id=id) for id in tags]
        else:
            tags = f.indirect_tag_set.all()

        # if request.user has chosen tags, restrict userlist to those users
        if tags:
            new_userlist = []
            for user in userlist:
                for tag in tags:
                    if user.tag_set.filter(id=tag.id).exists():
                        new_userlist.append(user)
                        break
            userlist = new_userlist

        # generate context table 
        # table = list of (user, score, [SolutionScore of problems[i] or None if not submited]
        table = []
        for user in userlist:
            ss_list = []
            score_sum = 0
            for prefix, problems in problem_list:
                ss_inner_list = []
                for problem in problems:
                    ss = None
                    if SolutionScore.objects.filter(problem=problem, user=user).exists():
                        ss = SolutionScore.objects.get(problem=problem, user=user)
                    ss_inner_list.append(ss)
                    if ss != None:
                        score_sum += ss.get_score()
                ss_list.append(ss_inner_list)
            row = [user, score_sum, ss_list]
            table.append(row)
        table.sort(key=lambda row: (-row[1], row[0].username))

        context = get_context(folder_path)
        context['problem_list'] = problem_list
        context['table'] = table
        context['selected_tags'] = tags
        return render(request, 'folder/ranking.html', context)

class ShowSolution(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        f.show_solution ^= 1
        f.save()
        messages.success(request,
                ('Włączono' if f.show_solution else 'Wyłączono') + ' rozwiązania/hinty/odpowiedzi!')
        return redirect('folder:edit', folder_path)

class ShowStats(StaffOnly, View):
    def post(self, request, folder_path):
        f = get_folder(folder_path)
        f.show_stats ^= 1
        f.save()
        messages.success(request,
                ('Włączono' if f.show_stats else 'Wyłączono') + ' statystyki!')
        return redirect('folder:edit', folder_path)

