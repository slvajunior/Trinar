from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    # Defina outras rotas para timeline, notificações, etc.
]
