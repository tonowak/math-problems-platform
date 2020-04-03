from django.db import models
from problems.models import Problem
from tags.models import Tag

class Folder(models.Model):
    parent      = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    folder_name = models.CharField(max_length=100)
    pretty_name = models.CharField(max_length=100)
    problem_set = models.ManyToManyField(Problem)
    tag_set     = models.ManyToManyField(Tag)

    def __str__(self):
        return self.pretty_name
