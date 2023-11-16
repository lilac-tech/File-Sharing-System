from django.contrib import admin
from .models import Announcement

# Register your models here.


class AnnouncementManager(admin.ModelAdmin):
    list_display = ('title', 'date_created', 'uploaded_by')


admin.site.register(Announcement, AnnouncementManager)