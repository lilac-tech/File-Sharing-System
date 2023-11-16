from django.db import models
from user.models import User


# Create your models here.


class Document(models.Model):
    """
    Document model

    Note:
        -The field comments is not mentioned in the model, 
        because it is created automatically by the 'Comment' model using 
        'related_name' argument in the 'document' field in the 'Comment' model.
    """
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=50)
    date_created = models.DateTimeField(verbose_name='date created', auto_now_add=True)
    size = models.FloatField()
    times_downloaded = models.IntegerField(default=0, blank=True, null=True)
    times_viewed = models.IntegerField(default=0)
    document = models.FileField(upload_to="documents")
    file_type = models.CharField(max_length=10)
    thumbnail = models.ImageField(upload_to="thumbnails", null=True)
    division = models.CharField(max_length=3, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Comment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    user_id = models.CharField(max_length=8)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)
