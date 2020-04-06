from django.urls import path

from . import views

app_name = 'tags'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.AddView.as_view(), name='add'), 
    path('<int:pk>/edit', views.EditView.as_view(), name='edit'),
]
