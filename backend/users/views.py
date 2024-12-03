from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserRegistrationForm
from django.urls import reverse
from users.models import UserProfile, Post
from django.contrib.auth.decorators import login_required
from .forms import UserProfileEditForm
import requests
from .forms import PostForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home:index")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home:index")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(reverse("users:login"))


@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    #  obitendo os posts do usuário logado

    user_posts = Post.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "users/profile.html",
        {
            "user_profile": user_profile,
            "user_posts": user_posts,
            "date_joined": request.user.date_joined,
        },
    )


@login_required
def edit_profile(request):
    try:
        user_profile = request.user.profile  
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileEditForm(
            request.POST, 
            request.FILES, 
            instance=user_profile
        )
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = UserProfileEditForm(instance=user_profile)

    return render(request, 'users/edit_profile.html', {'form': form})


def get_location_from_ip(ip):
    access_key = 'YOUR_API_KEY'  # Substitua com sua chave de API do ipstack
    url = f'http://api.ipstack.com/{ip}?access_key={access_key}'
    response = requests.get(url)
    data = response.json()
    location = data.get('city', 'Desconhecida')
    return location


@login_required
def create_post(request):
    # Recuperando o IP do usuário
    ip = request.META.get('REMOTE_ADDR')
    location = get_location_from_ip(ip)

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.location = location
            post.save()
            return redirect('home:index')
    else:
        form = PostForm()

    return render(request, 'users/create_post.html', {'form': form})
