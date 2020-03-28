from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from sceleapp.models import UserPost

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, help_text='Wajib, silahkan masukkan alamat email yang benar.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

class UserPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserPostForm, self).__init__(*args, **kwargs)
        self.fields['msg'].label = "Message"
        self.label_suffix = "*"

    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    msg = forms.CharField(widget=forms.Textarea(attrs={'id':'msg'}))

    class Meta:
        model = UserPost
        fields = ('subject', 'msg')