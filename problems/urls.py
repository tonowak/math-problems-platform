from django.urls import path

from . import views

app_name = 'problems'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.AddView.as_view(), name='add'), 
    path('<int:pk>/', views.DetailsView.as_view(), name='details'),
]
