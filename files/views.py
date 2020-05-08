from django.views import generic, View
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .models import SavedImage, save_image
from .forms import SubmitFilesTextForm
from users.permissions import StaffOnly

# add permissions
class IndexView(ListView):
    model = SavedImage
    template_name = "files/index.html"

class AddView(FormView):
    form_class = SubmitFilesTextForm
    template_name = "files/add.html"
    success_url = reverse_lazy("files:index")

    def post(self, request):
        form = self.get_form(self.get_form_class())
        files = request.FILES.getlist('files')
        if form.is_valid():
            for f in files:
                save_image(f, request.user, form.cleaned_data['description'])
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class PreviewView(View):
    def get(self, request, image_id):
        image = get_object_or_404(SavedImage, id=image_id).image
        return FileResponse(open(image.path, 'rb'), content_type='image/png') 
        # TODO: optimize for nginx
