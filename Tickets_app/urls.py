
from django.contrib import admin
from django.urls import path
from . import views   

urlpatterns = [
    path('', views.home, name='home'),
    path('train-list/', views.train_list, name='train_list'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),  
    path('trains/', views.train_list, name='train_list'),
    path('search/', views.search_trains, name='search_trains'),
    path('book/<str:train_id>/', views.book_train, name='book_train'),
    path('admin/', admin.site.urls),
    path("pnr/", views.pnr_status, name="pnr_status"),
    path("cancel/", views.cancel_ticket, name="cancel_ticket"),
    path("history/", views.my_bookings, name="my_bookings"),
    path("profile/", views.profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("logout/", views.logout, name="logout"),
    path("add-train/", views.add_train, name="add_train"),
    path("credit-card/", views.credit_card, name="credit_card"),
    path("net-banking/", views.net_banking, name="net_banking"),
    path("payment-process/", views.payment_process, name="payment_process"),
    path("ticket/", views.ticket, name="ticket"),
  
   
]  



