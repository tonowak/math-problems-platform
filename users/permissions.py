from django.contrib.auth.decorators import user_passes_test, login_required

staff_only = user_passes_test(lambda u: u.is_staff, login_url='users:login')



