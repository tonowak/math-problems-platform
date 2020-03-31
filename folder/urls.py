from django.urls import path

from . import views

app_name = 'folder'
urlpatterns = [
    path('<path:folder_path>/edit', views.EditView.as_view(), name='edit'),
    path('<path:folder_path>/add_folder', views.AddFolder.as_view(), name='add_folder'),
    path('<path:folder_path>/add_problem', views.AddProblem.as_view(), name='add_problem'),
    path('<path:folder_path>', views.IndexView.as_view(), name='index'),
]
