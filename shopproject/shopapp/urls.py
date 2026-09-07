from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('login/', views.login_view, name='login'),  
    path('signup/', views.user_signup, name='signup'), 
    path('logout/', views.user_logout, name='logout'), 
    path('user_home/', views.user_home, name='user_home'),  
    path('contact/', views.contact, name='contact'),  
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),    path('categories/', views.category_view, name='categories'), 
    path('search/', views.search, name='search'), 
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),  

]
