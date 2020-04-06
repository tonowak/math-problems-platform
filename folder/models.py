from django.db import models
from django.contrib.auth.models import User

from problems.models import Problem
from tags.models import Tag

class Folder(models.Model):
    parent      = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    folder_name = models.CharField(max_length=100)
    pretty_name = models.CharField(max_length=100)
    tag_set     = models.ManyToManyField(Tag)
    problem_set = models.ManyToManyField(Problem, through='ProblemPlace')
    created_by  = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.pretty_name

class ProblemPlace(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    place = models.IntegerField()
