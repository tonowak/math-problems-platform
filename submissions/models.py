from django.db import models
from django.contrib.auth.models import User

from problems.models import Problem, convert_string_to_number_list
from folder.models import Folder
from files.models import SavedImage

class Thread(models.Model):
    is_public  = models.BooleanField()
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_problem = models.ForeignKey(Problem, null=True, on_delete=models.SET_NULL)
    parent_folder  = models.ForeignKey(Folder, null=True, on_delete=models.SET_NULL)
    answer_checker = models.TextField(default='')

    # make sure that a Thread has a parent Folder *or* Problem
    def save(self, *args, **kwargs):
        pr = self.parent_problem
        fl = self.parent_folder
        assert (pr == None and fl != None) or (pr != None and fl == None)
        super().save(*args, **kwargs)

    def can_comment(self, user):
        return user.is_staff or self.is_public or self.created_by == user

    def get_answer_checker_list(self):
        return convert_string_to_number_list(self.answer_checker)

    def correct_answer(self):
        assert self.parent_problem != None
        model = convert_string_to_number_list(self.parent_problem.answer_checker)
        assert len(model) > 0
        check = convert_string_to_number_list(self.answer_checker)
        found = [False for x in model]
        for i in range(len(check)):
            for j in range(len(model)):
                if check[i] == model[j]:
                    found[j] = True
        for j in range(len(model)):
            if not found[j]:
                return False
        return True

class Comment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

class Attachment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    image = models.ForeignKey(SavedImage, on_delete=models.CASCADE)
