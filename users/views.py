from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import logout

# Create your views here.

def login_view(request):
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('users:login')
