from .views import login_view, logout_view, register_view
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLoginView.as_view(), name='logout'),

]
