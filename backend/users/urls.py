from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path(
        'micro-profile/<str:username>/', views.micro_profile,
        name='micro_profile'
        ),
]
