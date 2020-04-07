from django.contrib.auth.models import User 

for user in User.objects.all():
    user.is_staff = True
    user.save()
