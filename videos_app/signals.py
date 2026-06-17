import os
import shutil

import django_rq
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from videos_app.models import Video


@receiver(post_save, sender=Video)
def enqueue_video_processing(sender, instance, created, **kwargs):
    """Enqueues the FFMPEG processing job when a new video is uploaded."""
    if created:
        queue = django_rq.get_queue('low')
        queue.enqueue('videos_app.tasks.process_video', instance.id)


@receiver(post_delete, sender=Video)
def delete_video_files(sender, instance, **kwargs):
    """Deletes all media files associated with a video after it is
    removed from the database."""
    if instance.video_file and instance.video_file.name:
        original_path = instance.video_file.path
        if os.path.isfile(original_path):
            os.remove(original_path)

    if instance.thumbnail and instance.thumbnail.name:
        thumbnail_path = instance.thumbnail.path
        if os.path.isfile(thumbnail_path):
            os.remove(thumbnail_path)

    hls_dir = os.path.join(
        settings.MEDIA_ROOT, 'videos', str(instance.pk)
    )
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)
