from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-history/', views.attendance_history, name='attendance_history'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
]