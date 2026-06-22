from django import forms
from django.contrib import admin
from .models import Video


class VideoAdminForm(forms.ModelForm):
    """Admin form that makes video_file optional when editing existing videos."""

    class Meta:
        model = Video
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['video_file'].required = False


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""

    form = VideoAdminForm
