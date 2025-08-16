from django.urls import path
from . import views

app_name = 'root'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
]