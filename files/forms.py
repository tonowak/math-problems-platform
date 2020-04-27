from django import forms

class AddImagesForm(forms.Form):
    files = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    description = forms.CharField(max_length=100, required=False)

