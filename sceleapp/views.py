from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import render, redirect

from sceleapp.forms import RegisterForm

# Create your views here.
is_logged_in = False

def login(request):
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            uname = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=uname, password=raw_password)
            auth_login(request, user)
            registered = True
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})