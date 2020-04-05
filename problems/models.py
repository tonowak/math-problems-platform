from django.db import models

class Problem(models.Model):
    statement = models.TextField(default='')
    solution  = models.TextField(default='')
    hints     = models.TextField(default='')
    answer    = models.TextField(default='')

    def __str__(self):
        return self.statement[:20] + "..."
