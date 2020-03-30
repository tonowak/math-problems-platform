from django.db import models

class Folder(models.Model):
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

