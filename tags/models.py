from django.db import models

from problems.models import Problem

class Tag(models.Model):
    name = models.CharField(max_length=100)
    type_id = models.IntegerField(default=0)
    problems = models.ManyToManyField(Problem)

    def __str__(self):
        return self.name
