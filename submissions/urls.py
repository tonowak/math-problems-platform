from django.urls import path

from . import views

app_name = 'submissions'
urlpatterns = [
    path('<int:thread_id>', views.DetailsView.as_view(), name='details'),
]
