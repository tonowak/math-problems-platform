from django.urls import path

from . import views

app_name = 'folder'
urlpatterns = [
    path('<path:folder_path>/add', views.AddView.as_view(), name='add'),
    path('<path:folder_path>', views.IndexView.as_view(), name='index'),
]
