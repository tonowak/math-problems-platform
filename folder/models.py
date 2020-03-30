from django.db import models

class Folder(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    folder_name = models.CharField(max_length=100)
    pretty_name = models.CharField(max_length=100)

    def __str__(self):
        return self.pretty_name
