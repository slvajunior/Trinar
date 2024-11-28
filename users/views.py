from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.urls import reverse
from .forms import RegisterForm
from django.contrib.auth.views import LoginView


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta criada com sucesso!")
            return redirect('users:login')  # Redireciona para a página de login
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo {username}!')
                return redirect('home:index')  # Corrigido para o namespace 'home'
            else:
                messages.error(request, 'Credenciais inválidas.')
        else:
            messages.error(request, 'Erro ao autenticar.')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect(reverse('users:login'))


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
