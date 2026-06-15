import os
from django.conf import settings


def build_hls_path(movie_id, resolution, filename):
    """Builds the absolute filesystem path to an HLS file for a given video and resolution."""
    return os.path.join(settings.MEDIA_ROOT, 'videos', str(movie_id), resolution, filename)
