from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from users.models import Post
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification
from django.views.decorators.csrf import csrf_exempt


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
        # Pega o conteúdo da postagem
        post_content = request.POST.get("content")

        if post_content:  # Verifica se o conteúdo não está vazio
            # Cria o post e salva no banco de dados
            Post.objects.create(content=post_content, user=request.user)
            return redirect("home:index")
        else:
            return HttpResponse(
                "O conteúdo da postagem não pode ser vazio.", status=400
            )

    return render(request, "home/post_form.html")


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
        notification_type='like',
        user=post.user,  # Quem recebeu o like
        post=post,
        like_user=like_user  # O usuário que deu o like
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
    return render(request, "home/notifications.html", {
        "notifications": notifications})


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
