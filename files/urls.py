from django.urls import path

from . import views

app_name = 'files'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add', views.AddView.as_view(), name='add'),
    # path('<int:id>/delete', views.DeleteView.as_view(), name='delete'),
    path('<int:image_id>', views.PreviewView.as_view(), name='download'),
]
