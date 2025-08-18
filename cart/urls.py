from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('address/', views.address, name='address'),
    path('payment/', views.payment, name='payment'),
    path('orders/', views.orders, name='orders'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('cancel/<str:order_number>/', views.cancel_order, name='cancel_order'),
    path('reorder/<str:order_number>/', views.reorder, name='reorder'),
    path('track/<str:order_number>/', views.track_order, name='track_order'),
    path('invoice/<str:order_number>/', views.download_invoice, name='download_invoice'),
    path('admincart/', views.admin_cart_management, name='admin_cart_management'),
]