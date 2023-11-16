from django.db import models
from user.models import User

# Create your models here.
class Announcement(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(verbose_name='date created', auto_now_add=True)
    poster = models.ImageField(upload_to="posters", null=True, blank=True)
    division = models.CharField(max_length=3, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, auto_created=True)
