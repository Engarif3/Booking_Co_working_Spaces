from turtle import home
from . import views
from django.urls import path

urlpatterns = [
    path('',views.solid_login, name='solid_login'),
    path('login/',views.solid_login, name='solid_login'),
    path('logout/',views.logout, name='solid_logout'),
    path('create-space/', views.write_to_pod, name='text_input_form'),
    path('show-data/', views.show_user_data, name='show_pod_data'),
    path('all-data/', views.show_all_data, name='show_all_data'),
    
    path('space/delete/<str:uuid>/', views.delete_space, name='delete_space'),
    path('space/update/<str:uuid>/', views.update_space, name='update_space'),
    path('home/space/book/<uuid:uuid>/', views.space_booking, name='book_space'),
    path('space/confirm/<uuid:uuid>/', views.booking_confirmation, name='confirm_booking'),
    path('booking/success/', views.booking_success, name='booking_success'),
    path('show-bookings/', views.show_booking_data, name='show_bookings'),
    path('test-acl-access/', views.test_acl_access_view, name='test_acl_access'),
]
