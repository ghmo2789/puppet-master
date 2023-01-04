from django import forms


class clientForm(forms.Form):
    """
    A form Class for selecting clients to send tasks to
    """
    selected_clients = forms.BooleanField(label='clients', required=False)
    task = forms.NullBooleanField()
