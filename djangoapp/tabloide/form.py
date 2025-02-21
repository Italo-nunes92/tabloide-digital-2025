from django import forms
from .models import Store

class StoreForm(forms.Form):
    title = forms.ModelChoiceField(
        queryset=Store.objects.order_by('title').distinct('title'),
        empty_label="Selecione a cidade",
        label="Cidade"
    )