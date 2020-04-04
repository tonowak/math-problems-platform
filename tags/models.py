from django.db import models

from problems.models import Problem
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=100)
    type_id = models.IntegerField(default=0)
    problems = models.ManyToManyField(Problem)
    user_set = models.ManyToManyField(User)

    def __str__(self):
        return self.name
