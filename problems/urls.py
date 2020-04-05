from django.urls import path

from . import views

app_name = 'problems'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add', views.AddView.as_view(), name='add'), 
    path('<int:pk>/', views.DetailsView.as_view(), name='details'),
    path('<int:pk>/edit', views.EditView.as_view(), name='edit'),
    path('<int:pk>/delete', views.DeleteView.as_view(), name='delete'),
    path('<int:pk>/claim', views.ClaimView.as_view(), name='claim'),
]
