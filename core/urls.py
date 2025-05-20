from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='core/logged_out.html', next_page='home'), name='logout'),
    
    # Маршруты для пациентов
    path('appointment/make/', views.make_appointment, name='make_appointment'),
    path('appointments/my/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    
    # Маршруты для администратора
    path('dashboard/', views.admin_panel, name='admin_panel'),
    path('dashboard/appointments/', views.admin_appointments, name='admin_appointments'),
    path('dashboard/doctors/', views.admin_doctors, name='admin_doctors'),
    path('dashboard/doctors/add/', views.admin_add_doctor, name='admin_add_doctor'),
    path('dashboard/doctors/edit/<int:doctor_id>/', views.admin_edit_doctor, name='admin_edit_doctor'),
    path('dashboard/doctors/delete/<int:doctor_id>/', views.admin_delete_doctor, name='admin_delete_doctor'),
    
    # Маршруты для управления пользователями
    path('dashboard/users/', views.admin_users, name='admin_users'),
    path('dashboard/users/add/', views.admin_add_user, name='admin_add_user'),
    path('dashboard/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('dashboard/users/toggle-role/<int:user_id>/', views.admin_toggle_user_role, name='admin_toggle_user_role'),
    path('dashboard/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
] 