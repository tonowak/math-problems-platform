from django.shortcuts import render, redirect


def index(request):
    if request.user.is_authenticated:
        return redirect('folder:index', 'all')
    return redirect('users:login')
