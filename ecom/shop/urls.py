from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home' ),
    path('Cart/', views.cart, name='cart' ),
    path('Checkout/', views.checkout, name='checkout' ),
    path('update_item/', views.updateItem, name='updateItem'),
    path('LoginUser/', views.LoginUser, name='LoginUser'),
    path('RegisterUser/', views.RegisterUser, name='RegisterUser'),
    path('LogoutUser/', views.LogoutUser, name='LogoutUser'),
    path('viewProduct/', views.viewProduct, name='viewProduct'),
    path('viewProduct/<int:productid>/', views.viewProduct, name='viewProduct'),
    path('makePaymentresponse/',views.response)
    
    
]