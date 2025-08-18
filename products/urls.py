from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('product_list', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/add_review/', views.add_review, name='add_review'),
]