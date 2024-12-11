from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http import HttpResponse
from .models import Notification
from django.urls import reverse
from .forms import CommentForm
from .models import Comment, Post
from .models import Follow
import re


def convert_links_to_html(content):
    # Expressão regular para encontrar URLs
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    # Substituir as URLs encontradas por tags <a>
    content_with_links = re.sub(
        url_pattern, r'<a href="\g<0>" target="_blank">\g<0></a>', content
    )
    return content_with_links


def convert_mentions_to_html(content):
    # Expressão regular para encontrar menções de usuários
    mention_pattern = r"@([a-zA-Z0-9_áéíóúãâêôãçáàü]+)"

    # Substituir as menções pelo link do perfil do usuário
    content_with_mentions = re.sub(
        mention_pattern,
        lambda match: f'<a href="{reverse("users:micro_profile", args=[match.group(1)])}">@{match.group(1)}</a>',
        content,
    )
    return content_with_mentions


@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect("home:notifications")


@login_required
def index(request):
    # Obter os usuários seguidos pelo usuário atual
    followed_users = Follow.objects.filter(follower=request.user).values_list(
        "following_id", flat=True
    )
    # Incluir o próprio usuário na lista
    user_ids = list(followed_users) + [request.user.id]

    # Obter os posts dos usuários seguidos e do próprio usuário
    posts = Post.objects.filter(user_id__in=user_ids).order_by("-created_at")

    for post in posts:
        # Verificar se o usuário curtiu cada post
        post.user_has_liked = post.likes.filter(id=request.user.id).exists()

        # Aplicar a conversão de links e menções no conteúdo do post
        post.content = convert_links_to_html(post.content)
        post.content = convert_mentions_to_html(post.content)  # Adicionando as menções
        post.is_html = True  # Indicar que o conteúdo já é HTML

    # Contar notificações não lidas
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Adicionar posts e contador ao contexto
    context = {
        "posts": posts,
        "unread_count": unread_count,
    }

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
            new_post = Post.objects.create(
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
            new_post = Post.objects.create(content=post_content, user=request.user)

            # Detecta menções no conteúdo do post
            mentions = re.findall(
                r"@(\w+)", post_content
            )  # Encontra menções com o símbolo @
            for mention in mentions:
                try:
                    mention_user = User.objects.get(
                        username=mention
                    )  # Busca o usuário mencionado
                    Notification.objects.create(
                        notification_type="mention",
                        user=mention_user,  # O usuário que será notificado
                        post=new_post,  # O post em que foi feita a menção
                        mention_user=request.user,  # O usuário que fez a menção
                    )
                except User.DoesNotExist:
                    continue  # Caso o usuário mencionado não exista, ignora

            return redirect("home:index")
        else:
            return HttpResponse(
                "O conteúdo da postagem não pode ser vazio.", status=400
            )

    return render(request, "home/index.html")


@login_required
def toggle_like(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if post.likes.filter(id=user.id).exists():
            # Descurtir
            post.likes.remove(user)
            user_has_liked = False
        else:
            # Curtir
            post.likes.add(user)
            user_has_liked = True

            # Função para notificar o autor do post sobre o like
            create_like_notification(user, post)

        return JsonResponse(
            {"likes_count": post.likes.count(), "user_has_liked": user_has_liked}
        )

    return JsonResponse({"error": "Invalid request"}, status=400)


def toggle_repost(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)

        # Verifica se o usuário já repostou o post
        if post.reposts.filter(id=request.user.id).exists():
            # Se já repostou, desfaz o repost
            post.reposts.remove(request.user)
            user_has_reposted = False
        else:
            # Se não repostou, cria o repost
            post.reposts.add(request.user)
            user_has_reposted = True

        return JsonResponse({
            'user_has_reposted': user_has_reposted,
            'repost_count': post.reposts.count()
        })


def create_like_notification(like_user, post):
    # Cria uma notificação para o usuário que recebeu o like
    notification = Notification.objects.create(
        notification_type="like",
        user=post.user,  # Quem recebeu o like
        post=post,
        like_user=like_user,  # O usuário que deu o like
    )
    return notification


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
    else:
        comment_form = CommentForm()

    return render(
        request, "home/post_detail.html", {"post": post, "comment_form": comment_form}
    )


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    comment_content = request.POST.get('content')

    # Criando o comentário
    comment = Comment.objects.create(
        user=request.user,
        post=post,
        content=comment_content
    )

    # Criando a notificação para o dono do post
    Notification.objects.create(
        notification_type="comment",
        user=post.user,  # Usuário que recebe a notificação (dono do post)
        post=post,  # Post no qual o comentário foi feito
        comment_user=request.user,  # Usuário que fez o comentário
        comment=comment  # Agora associamos o comentário à notificação
    )

    # Redirecionar ou renderizar a resposta
    return redirect('home:index')


@login_required
def notifications(request):
    # Buscar notificações do usuário
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    # Marcar todas as notificações como lidas
    notifications.filter(is_read=False).update(is_read=True)

    # Debug opcional para confirmar as notificações no console
    print(f"Notificações: {notifications}")

    return render(request, "home/notifications.html", {"notifications": notifications})


@login_required
def retrinar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    new_post = Post.objects.create(  # type:ignore
        user=request.user, content=post.content, is_retrinar=True, original_post=post
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
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect("users:profile", username=user_to_unfollow.username)


@login_required
def followers_list(request):
    followers = Follow.objects.filter(following=request.user)
    return render(request, "users/followers_list.html", {"followers": followers})


def get_unread_notifications_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()
