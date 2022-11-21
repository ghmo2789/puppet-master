from django import forms

class clientForm(forms.Form):
    selected_clients = forms.BooleanField(label='clients', required=False)
    task = forms.NullBooleanField()

