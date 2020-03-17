from django.contrib.auth import login as auth_login, authenticate, logout
from django.shortcuts import render, redirect

from sceleapp.forms import RegisterForm

# Create your views here.

def dashboard(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'dashboard.html')
    else:
        return login(request)


def login(request):
    return render(request, 'auth/login.html')

# sourcecode: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
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
    return render(request, 'auth/register.html', {'form': form})