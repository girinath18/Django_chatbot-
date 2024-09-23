#from django.db import models

# Create your models here.
from django.db import models

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_content = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ChatHistory(models.Model):
    session_id = models.CharField(max_length=255)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

