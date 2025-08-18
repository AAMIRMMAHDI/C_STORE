from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('favorites/', views.favorites, name='favorites'),
    path('adminusers/', views.admin_user_management, name='admin_user_management'),
]