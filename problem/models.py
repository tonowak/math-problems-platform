from django.db import models

# Create your models here.

class Problem(models.Model):
    content = models.TextField()

    def __str__(self):
        return self.content[:20] + "..."

class SolutionTag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self)
        return self.name

class SourceTag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self)
        return self.name
