import os
import subprocess
from django.conf import settings

RESOLUTIONS = {
    '480p': 'scale=854:480',
    '720p': 'scale=1280:720',
    '1080p': 'scale=1920:1080',
}


def get_output_dir(video_id, resolution):
    """Returns the absolute path to the output directory for a given video and resolution."""
    return os.path.join(settings.MEDIA_ROOT, 'videos', str(video_id), resolution)


def convert_to_hls(input_path, output_dir, scale):
    """Converts a video file to HLS format at the given scale and writes segments to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-vf', scale,
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-hls_segment_filename', os.path.join(output_dir, '%03d.ts'),
        os.path.join(output_dir, 'index.m3u8'),
    ], check=True)


def generate_thumbnail(input_path, output_path):
    """Extracts a single frame at 00:00:01 from the video and saves it as a JPEG thumbnail."""
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-ss', '00:00:01',
        '-vframes', '1',
        output_path,
    ], check=True)


def process_video(video_id):
    """Converts a video to HLS for all resolutions and generates a thumbnail. Runs as an RQ background job."""
    from .models import Video
    video = Video.objects.get(pk=video_id)
    input_path = video.video_file.path
    base_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(video_id))

    for resolution, scale in RESOLUTIONS.items():
        convert_to_hls(input_path, get_output_dir(video_id, resolution), scale)

    thumbnail_path = os.path.join(base_dir, 'thumbnail.jpg')
    generate_thumbnail(input_path, thumbnail_path)

    video.thumbnail = f'videos/{video_id}/thumbnail.jpg'
    video.save(update_fields=['thumbnail'])
