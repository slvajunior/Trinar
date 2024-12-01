from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserRegistrationForm
from django.urls import reverse
from users.models import UserProfile, Post
from django.contrib.auth.decorators import login_required


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
