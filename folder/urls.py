from django.urls import path

from . import views

app_name = 'folder'
urlpatterns = [
    path('<path:folder_path>/edit', views.EditView.as_view(), name='edit'),
    path('<path:folder_path>/add_folder', views.AddFolder.as_view(), name='add_folder'),
    path('<path:folder_path>/edit_folder_name', views.EditFolderName.as_view(), name='edit_folder_name'),
    path('<path:folder_path>/delete_folder', views.DeleteFolder.as_view(), name='delete_folder'),
    path('<path:folder_path>/add_problem', views.AddProblem.as_view(), name='add_problem'),
    path('<path:folder_path>/delete_problem', views.DeleteProblem.as_view(), name='delete_problem'),
    path('<path:folder_path>/edit_tags', views.EditTags.as_view(), name='edit_tags'),
    path('<path:folder_path>', views.IndexView.as_view(), name='index'),
]
