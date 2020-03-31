from django.db import models

class Problem(models.Model):
    content = models.TextField()

    def __str__(self):
        return self.content[:20] + "..."
