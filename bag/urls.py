from django.urls import path
from .views import (
    index, milk_page, fruits_page, vegetables_page,
    product_detail, add_to_cart, view_cart,
    checkout, login_view, logout_view, register_view, 
    remove_from_cart, update_cart_quantity, search,
    place_order, payment, order_success,profile_view,
    toggle_favorite
)


urlpatterns = [
    path('', index, name='index'),

    path('login/', login_view, name='login'),
    path('logout/',logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('search/', search, name='search'),
    path('milk/', milk_page, name='milk'),
    path('fruits/', fruits_page, name='fruits'),
    path('vegetables/', vegetables_page, name='vegetables'),
    path('profile/', profile_view, name='profile'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('cart/', view_cart, name='view_cart'),
    path('checkout/',checkout, name='checkout'),
    path('update-cart/<int:product_id>/<str:action>/', update_cart_quantity, name='update_cart_quantity'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('place-order/', place_order, name='place_order'),
    path('payment/<int:order_id>/', payment, name='payment'),
    path('order-success/', order_success, name='order_success'),
    path('toggle-favorite/<int:product_id>/',toggle_favorite, name='toggle_favorite'),
    path('favorite/<int:product_id>/',toggle_favorite, name='toggle_favorite'),
]
