from django.shortcuts import render, reverse
from django.views.generic.edit import FormView
from django.contrib import messages

from .models import Thread, Comment, Attachment
from users.permissions import FolderAccess, ProblemAccess
from files.forms import SubmitFilesTextForm
from files.models import save_image
from folder.models import Folder, ProblemPlace, get_folder
from folder.views import get_context
from problems.models import Problem
from tiled_math.views import ArgSuccessUrlMixin

class FileFormView(FormView):
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')
        if form.is_valid():
            messages.success(request, 'Wysłano!')
            return self.form_valid(form, files)
        else:
            return self.form_invalid(form)

def convert_threads_to_lists(threads, user):
    # returns a list of (thread, list of (comment, comment_files), can_comment)
    ret = []
    for thread in threads:
        comments = []
        for comment in Comment.objects.filter(thread=thread).order_by('id'):
            files = []
            for attachment in Attachment.objects.filter(comment=comment):
                files.append(attachment.image)
            comments.append((comment, files))
        ret.append((thread, comments, thread.can_comment(user)))
    return ret

class SubmitFromFolderView(ArgSuccessUrlMixin, FolderAccess, FileFormView):
    form_class = SubmitFilesTextForm
    template_name = 'submissions/folder_submit.html'
    success_url = ('folder:submissions', 'folder_path')

    def dfs(self, user, f, threads):
        for th in Thread.objects.filter(parent_folder=f, is_public=True)  \
                | Thread.objects.filter(parent_folder=f, created_by=user):
            threads.append(th)
        for pp in ProblemPlace.objects.filter(folder=f):
            for th in Thread.objects.filter(parent_problem=pp.problem, is_public=True)  \
                    | Thread.objects.filter(parent_problem=pp.problem, created_by=user):
                threads.append(th)

        for son in Folder.objects.filter(parent=f):
            self.dfs(user, son, threads)

    def get_threads(self, user, f):
        threads = []
        self.dfs(user, f, threads)
        threads = sorted(threads, key=lambda t: (not t.is_public, -t.id))
        return threads
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_path = self.kwargs.get(self.success_url[1])
        folder = get_folder(folder_path)
        context.update(get_context(folder_path))
        user = self.request.user
        context['threads'] = convert_threads_to_lists(self.get_threads(user, folder), user)
        print(context['threads'])
        return context

    def form_valid(self, form, files):
        folder = get_folder(self.kwargs.get(self.success_url[1]))
        user = self.request.user
        make_public = user.is_staff

        t = Thread(parent_folder=folder, created_by=user, is_public=make_public)
        t.save()
        c = Comment(thread=t, created_by=user, description=form.cleaned_data['description'])
        c.save()
        for f in files:
            a = Attachment(comment=c, image=save_image(f))
            a.save()
        return super().form_valid(form)

class SubmitFromProblemView(ArgSuccessUrlMixin, ProblemAccess, FileFormView):
    form_class = SubmitFilesTextForm
    template_name = 'submissions/problem_submit.html'
    success_url = ('problems:submissions', 'pk')

    def get_threads(self, user, problem):
        threads = []
        for th in Thread.objects.filter(parent_problem=problem, is_public=True)  \
                | Thread.objects.filter(parent_problem=problem, created_by=user):
            threads.append(th)
        threads = sorted(threads, key=lambda t: (not t.is_public, -t.id))
        return threads
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = Problem.objects.get(id=self.kwargs.get(self.success_url[1]))
        user = self.request.user
        context['threads'] = convert_threads_to_lists(self.get_threads(user, problem), user)
        context['problem'] = problem
        context['solved_task'] = user.problem_set.filter(id=problem.id).exists()
        return context

    def form_valid(self, form, files):
        user = self.request.user
        make_public = user.is_staff
        problem = Problem.objects.get(id=self.kwargs.get(self.success_url[1]))

        t = Thread(parent_problem=problem, created_by=user, is_public=make_public)
        t.save()
        c = Comment(thread=t, created_by=user, description=form.cleaned_data['description'])
        c.save()
        for f in files:
            a = Attachment(comment=c, image=save_image(f))
            a.save()
        return super().form_valid(form)

class DetailsView(ArgSuccessUrlMixin, FileFormView):
    form_class = SubmitFilesTextForm
    template_name = 'submissions/details.html'
    success_url = ('submissions:details', 'thread_id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        thread = Thread.objects.get(id=self.kwargs.get(self.success_url[1]))
        context['threads'] = convert_threads_to_lists([thread], user)
        if thread.parent_problem:
            back_url = reverse('problems:index', kwargs={'pk': thread.parent_problem.id})
        else:
            back_url = reverse('folder:submissions', kwargs={'folder_path': thread.parent_folder.get_path()})
        context['back_url'] = back_url
        return context

    def form_valid(self, form, files):
        user = self.request.user
        make_public = user.is_staff
        t = Thread.objects.get(id=self.kwargs.get(self.success_url[1]))

        c = Comment(thread=t, created_by=user, description=form.cleaned_data['description'])
        c.save()
        for f in files:
            a = Attachment(comment=c, image=save_image(f))
            a.save()
        return super().form_valid(form)
