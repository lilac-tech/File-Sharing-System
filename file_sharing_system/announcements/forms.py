from .models import Announcement
from django import forms


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'division', 'poster')
