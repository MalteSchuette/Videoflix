import os
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from videos_app.models import Video
from .serializers import VideoSerializer


class VideoListView(APIView):
    def get(self, request):
        """Returns a list of all videos with their metadata."""
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


def build_hls_path(movie_id, resolution, filename):
    """Builds the absolute filesystem path to an HLS file for a given video and resolution."""
    return os.path.join(settings.MEDIA_ROOT, 'videos', str(movie_id), resolution, filename)


class HLSPlaylistView(APIView):
    def get(self, request, movie_id, resolution):
        """Returns the HLS master playlist file for the given video and resolution."""
        path = build_hls_path(movie_id, resolution, 'index.m3u8')
        if not os.path.exists(path):
            raise Http404
        return FileResponse(open(path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    def get(self, request, movie_id, resolution, segment):
        """Returns a single HLS video segment for the given video and resolution."""
        path = build_hls_path(movie_id, resolution, os.path.basename(segment))
        if not os.path.exists(path):
            raise Http404
        return FileResponse(open(path, 'rb'), content_type='video/MP2T')
