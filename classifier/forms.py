from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class MessageForm(forms.Form):
    message = forms.CharField(label='Message to classify',
                              widget=forms.Textarea(attrs={'id': 'message-text'}),
                              min_length=20)