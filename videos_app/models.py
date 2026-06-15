from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq


class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
    category = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/original/')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Returns the video title as its string representation."""
        return self.title


@receiver(post_save, sender=Video)
def enqueue_video_processing(sender, instance, created, **kwargs):
    """Enqueues the FFMPEG processing job when a new video is uploaded."""
    if created:
        queue = django_rq.get_queue('default')
        queue.enqueue('videos_app.tasks.process_video', instance.id)
