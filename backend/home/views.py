from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from users.models import Post
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


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


@login_required
def curtir_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
                message = 'Like removido'
            else:
                post.likes.add(request.user)
                message = 'Like adicionado'

                # Criar a notificação
                Notification.objects.create(
                    user=post.user,
                    post=post,
                    notification_type='like'
                )

            return JsonResponse({'likes': post.likes.count(), 'message': message})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post não encontrado'}, status=404)
    return JsonResponse({'error': 'Método inválido'}, status=400)


@login_required
def post_detail(request, post_id):
    #  Busca o post pelo ID ou retorna 404 se não encontrado
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'home/post_detail.html', {'post': post})


@login_required
def notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'home/notifications.html', {
        'notifications': notifications
        }
    )







@login_required
def retrinar_post(request, post_id):
    # Recuperar o post pelo ID
    post = get_object_or_404(Post, id=post_id)

    # Criar o retrin post (assumindo um modelo para guardar os reposts)
    new_post = Post.objects.create(  # type:ignore
        user=request.user,
        content=post.content,
        is_retrinar=True,
        original_post=post
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Post retrinado com sucesso!'
        }
    )
