from django.urls import path
from . import views

app_name = 'user_orders'

urlpatterns = [
    path('', views.my_orders, name='my_orders'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]
