from django import forms
from .models import Store

class StoreForm(forms.Form):
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        label="Selecione a cidade",
    )