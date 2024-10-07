from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import chat_history_view



urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('chat/', views.chat_view, name='chat_view'),
    path('chat-history/', chat_history_view, name='chat_history'),
    path('upload/', views.upload_file, name='upload_file'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
