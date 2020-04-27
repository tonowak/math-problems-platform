from django.db import models
from django.contrib.auth.models import User

class SavedImage(models.Model):
    upload_to = 'images'
    image = models.ImageField(upload_to=upload_to)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.image.name
    def size_str(self):
        try:
            sz = self.image.size
        except:
            return "ERROR"
        KB = 1024
        MB, GB = KB ** 2, KB ** 3
        unit = {1: 'B', KB: 'KB', MB: 'MB', GB: 'GB'}
        for limit in [GB, MB, KB, 1]:
            if sz >= limit:
                return "{:.2f}".format(sz / limit) + ' ' + unit[limit]
                break
        return "ERROR"

def save_image(image, uploader=None, description=''):
    saved = SavedImage()
    saved.created_by = uploader
    saved.description = description
    saved.save()
    saved.image = image
    saved.image.name = str(saved.id)
    saved.save()

    print(saved.id, saved.image.path)
