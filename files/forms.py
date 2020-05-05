from django import forms

class SubmitFilesTextForm(forms.Form):
    files = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    description = forms.CharField(required=False, widget=forms.Textarea)

