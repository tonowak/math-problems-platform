from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    statement = models.TextField(default='')
    solution  = models.TextField(default='')
    hints     = models.TextField(default='')
    answer    = models.TextField(default='')
    claiming_user_set = models.ManyToManyField(User, related_name='problem_set')
    created_by  = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='problems_created')

    def __str__(self):
        return self.statement[:20] + "..."
