from django.urls import path
from .views import chat_view, upload_file

urlpatterns = [
    path('chat/', chat_view, name='chat'),
    path('upload_file/', upload_file, name='upload_file'),
    # Add other URL patterns as needed
]


