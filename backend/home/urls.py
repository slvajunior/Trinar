from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('post/', views.post, name='post'),
    path('retrinar/<int:post_id>/', views.retrinar_post, name='retrinar'),
    path("post_detail/<int:post_id>/", views.post_detail, name="post_detail"),
    path('notifications/', views.notifications, name='notifications'),
    path("toggle-like/", views.toggle_like, name="toggle_like"),
    path('search/', views.search, name='search'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('followers/', views.followers_list, name='followers_list'),
    path(
        'notifications/mark_as_read/<int:notification_id>/',
        views.mark_as_read, name='mark_as_read'),

]
