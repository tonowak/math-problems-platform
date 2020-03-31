from django.urls import path

from . import views

app_name = 'problems'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.AddView.as_view(), name='add'), 
    path('<int:pk>/', views.DetailsView.as_view(), name='details'),
    path('<int:pk>/edit', views.EditView.as_view(), name='edit'),
    path('<int:pk>/edit/statement', views.EditStatementView.as_view(), name='edit_statement'),
    path('tags/', views.TagsView.as_view(), name='tags'),
    path('tags/add/solution', views.AddSolutionTagView.as_view(), name='add_solution_tag'),
    path('tags/add/source', views.AddSourceTagView.as_view(), name='add_source_tag'),
]
