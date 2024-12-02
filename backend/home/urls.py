from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('post/', views.post, name='post'),
    path('curtir/<int:post_id>/', views.curtir_post, name='curtir_post'),
    path('retrinar/<int:post_id>/', views.retrinar_post, name='retrinar'),
    path("post_detail/<int:post_id>/", views.post_detail, name="post_detail"),
    path('notifications/', views.notifications, name='notifications'),
]
