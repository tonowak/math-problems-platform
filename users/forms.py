from django import forms

class SetSolutionScoreForm(forms.Form):
    problem = forms.IntegerField(required=True)
    score = forms.IntegerField(required=True)

