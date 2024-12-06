from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserRegistrationForm
from django.urls import reverse
from users.models import UserProfile, Post
from django.contrib.auth.decorators import login_required
from .forms import UserProfileEditForm
import requests
from .forms import PostForm
from home.models import Follow
from django.contrib.auth import get_user_model


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


def get_location_from_ip(ip):
    access_key = "YOUR_API_KEY"  # Substitua com sua chave de API do ipstack
    url = f"http://api.ipstack.com/{ip}?access_key={access_key}"
    response = requests.get(url)
    data = response.json()
    location = data.get("city", "Desconhecida")
    return location


@login_required
def create_post(request):
    # Recuperando o IP do usuário
    ip = request.META.get("REMOTE_ADDR")
    location = get_location_from_ip(ip)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.location = location
            post.save()
            return redirect("home:index")
    else:
        form = PostForm()

    return render(request, "users/create_post.html", {"form": form})


# View para exibir o perfil de um usuário
def micro_profile(request, username):
    # Buscar o usuário pelo username
    user = get_object_or_404(get_user_model(), username=username)
    user_profile = UserProfile.objects.get(user=user)
    user_posts = Post.objects.filter(user=user).order_by("-created_at")
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    is_following = Follow.objects.filter(
        follower=request.user,
        following=user).exists()

    return render(
        request,
        "users/profile.html",
        {
            "user_profile": user_profile,
            "user_posts": user_posts,
            "date_joined": user.date_joined,
            "born": user_profile.born,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
        },
    )


@login_required
def profile(request, username=None):
    # Se 'username' não for passado, pega o perfil do usuário logado
    if username:
        user = get_object_or_404(get_user_model(), username=username)
    else:
        user = request.user

    # Obtendo o perfil do usuário associado (UserProfile)
    user_profile = get_object_or_404(UserProfile, user=user)

    # Verificar se o usuário logado está visualizando seu próprio perfil
    is_owner = request.user == user  # O usuário logado é o dono do perfil?

    # Verificar se o usuário logado segue o perfil visualizado
    is_following = Follow.objects.filter(
        follower=request.user,
        following=user).exists()

    # Obtendo os posts do usuário visualizado
    user_posts = Post.objects.filter(user=user).order_by("-created_at")

    # Contagem de seguidores e seguindo do perfil visualizado
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    return render(
        request,
        "users/profile.html",
        {
            "user_profile": user_profile,  # Perfil completo (UserProfile)
            "user_posts": user_posts,
            "date_joined": user.date_joined,  # Data de entrada do User
            "born": user_profile.born,  # Data de nascimento do UserProfile
            "followers_count": followers_count,
            "following_count": following_count,
            "is_owner": is_owner,
            "is_following": is_following,
        },
    )


@login_required
def edit_profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        form = UserProfileEditForm(
            request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
            return redirect("users:profile", username=request.user.username)
    else:
        form = UserProfileEditForm(instance=user_profile)

    return render(request, "users/edit_profile.html", {"form": form})
