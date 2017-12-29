from django import forms

from .models import *

class NewAnalysisForm(forms.ModelForm):

    class Meta:
        model = DatapullId
        fields = ('pullname','pullquery','pulltype','pullsource','pullby',)
