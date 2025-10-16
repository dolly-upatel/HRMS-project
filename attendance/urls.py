from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from employees import views

def home(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-history/', views.attendance_history, name='attendance_history'),
    path('profile/', views.profile, name='profile'),
]

# Add media URLs in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)