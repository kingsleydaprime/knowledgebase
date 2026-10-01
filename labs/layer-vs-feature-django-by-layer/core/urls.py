# core/urls.py
from django.urls import path

from .views import orders, users

urlpatterns = [
    path("orders/", orders.order_list),
    path("users/", users.user_list),
]
