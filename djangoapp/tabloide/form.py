from django import forms
from .models import Store

class StoreForm(forms.Form):
    store = forms.ModelChoiceField(
        queryset=Store.objects.all().order_by('title'),
        label="Selecione a cidade",
        empty_label="Selecione uma cidade",
    )