from django.db import models
from datetime import datetime

# Create your models here.

class FileMetadata(models.Model):
    name = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True, blank=True)