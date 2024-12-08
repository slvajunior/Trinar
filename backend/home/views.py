from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from users.models import Post
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Follow
from django.contrib.auth import get_user_model


@login_required
def index(request):
    posts = Post.objects.all()
    for post in posts:
        post.user_has_liked = post.likes.filter(id=request.user.id).exists()

    context = {"posts": posts}
    return render(request, "home/index.html", context)


@login_required
def post(request):
    if request.method == "POST":
        # Verifica se é um repost
        original_post_id = request.POST.get("original_post_id")
        if original_post_id:
            # Tenta encontrar o post original
            original_post = get_object_or_404(Post, id=original_post_id)
            # Cria um novo post com referência ao post original
            Post.objects.create(  # Criação direta sem a variável new_post
                user=request.user, original_post=original_post
            )

            # Cria a notificação para o autor do post original
            Notification.objects.create(
                notification_type="repost",
                user=original_post.user,  # Destinatário: autor do post original
                post=original_post,
                repost_user=request.user,  # Quem repostou
            )
            return redirect("home:index")

        # Caso seja um novo post
        post_content = request.POST.get("content")
        if post_content:  # Verifica se o conteúdo não está vazio
            Post.objects.create(content=post_content, user=request.user)
            return redirect("home:index")
        else:
            return HttpResponse(
                "O conteúdo da postagem não pode ser vazio.", status=400
            )

    return render(request, "home/index.html")


@csrf_exempt  # Se você estiver usando Ajax e não enviar CSRF token
def toggle_like(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)  # Descurtir
            user_has_liked = False
        else:
            post.likes.add(user)  # Curtir
            user_has_liked = True

            create_like_notification(user, post)

        return JsonResponse(
            {"likes_count": post.likes.count(), "user_has_liked": user_has_liked}
        )

    return JsonResponse({"error": "Invalid request"}, status=400)


def create_like_notification(like_user, post):
    # Cria uma notificação para o usuário que recebeu o like
    notification = Notification.objects.create(
        notification_type="like",
        user=post.user,  # Quem recebeu o like
        post=post,
        like_user=like_user,  # O usuário que deu o like
    )
    return notification


@login_required
def post_detail(request, post_id):
    #  Busca o post pelo ID ou retorna 404 se não encontrado
    post = get_object_or_404(Post, id=post_id)
    return render(request, "home/post_detail.html", {"post": post})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    print(f"Notificações: {notifications}")
    return render(
        request, "home/notifications.html", {"notifications": notifications})


@login_required
def retrinar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    new_post = Post.objects.create(  # type:ignore
        user=request.user,
        content=post.content,
        is_retrinar=True,
        original_post=post
    )

    context = {"new_post": new_post}

    return JsonResponse(
        {
            "status": "success",
            "message": "Post retrinado com sucesso!",
            "contex": context,
        }
    )


def search(request):
    query = request.GET.get("q", "")
    users = User.objects.filter(username__icontains=query)[:5]
    posts = Post.objects.filter(text__icontains=query)[:5]

    user_results = [{"username": user.username, "id": user.id} for user in users]
    post_results = [{"text": post.text[:100], "id": post.id} for post in posts]

    results = {"users": user_results, "posts": post_results}

    return JsonResponse(results)


@login_required
def follow_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(get_user_model(), id=user_id)

        # Verificar se já existe um relacionamento de seguir
        if not Follow.objects.filter(
            follower=request.user, following=target_user
        ).exists():
            # Criar o relacionamento de seguir
            Follow.objects.create(follower=request.user, following=target_user)

            # Criar a notificação para "seguir"
            Notification.objects.create(
                notification_type="follow",
                user=target_user,  # Quem está recebendo a notificação
                follower=request.user,  # Quem começou a seguir
            )

        return redirect("users:profile", username=target_user.username)


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(get_user_model(), id=user_id)
    Follow.objects.filter(
        follower=request.user,
        following=user_to_unfollow).delete()
    return redirect("users:profile", username=user_to_unfollow.username)


@login_required
def followers_list(request):
    followers = Follow.objects.filter(following=request.user)
    return render(request, "users/followers_list.html", {"followers": followers})
