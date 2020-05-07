from django.shortcuts import render, redirect, reverse

def index(request):
    if request.user.is_authenticated:
        return redirect('folder:index', 'all')
    return redirect('users:login')

class ArgSuccessUrlMixin(object):
    def get_success_url(self):
        assert len(self.success_url) == 2
        return reverse(self.success_url[0], kwargs={
            self.success_url[1]: self.kwargs.get(self.success_url[1])
        })

