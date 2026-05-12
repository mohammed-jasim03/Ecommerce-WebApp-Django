from django.urls import path
from .import views
from .views import register_user, check_username, add_to_wishlist,view_wishlist




urlpatterns = [
    path('',views.main_home,name='main_home'),
    path('products/brand/<str:brand_name>/', views.product_by_brand, name='product_by_brand'),
    path('category/<str:category_name>/', views.product_list_by_category, name='product_by_category'),
    path('Product/<int:pk>/', views.product, name='product_detail'),
    path('home1/',views.home, name='home'),
    path('about/',views.about, name='about'),
    path('login/',views.login_user, name='login'),
    path('logout/',views.logout_user, name='logout'),
    path('register/',views.register_user, name='register'),
    path('check_username/', check_username, name='check_username'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_info/', views.update_info, name='update_info'),
    path('update_user/', views.update_user, name='update_user'),
    path('Product/<int:pk>',views.product, name='product'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('category/<str:dd>',views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('add_to_wishlist/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', view_wishlist, name='view_wishlist'),
    
] 
