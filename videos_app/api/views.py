import os
from django.http import FileResponse, Http404
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.views import APIView

from videos_app.models import Video
from .serializers import VideoSerializer
from ..utils import build_hls_path


class VideoListView(APIView):
    """Returns a list of all available videos."""

    def get(self, request):
        """Returns a list of all videos with their metadata."""
        videos = Video.objects.all()
        serializer = VideoSerializer(
            videos, many=True, context={'request': request}
        )
        response = Response(serializer.data)
        response.set_cookie('csrftoken', get_token(request), samesite='Lax')
        return response


class HLSPlaylistView(APIView):
    """Serves the HLS master playlist for a given video and resolution."""

    def get(self, request, movie_id, resolution):
        """Returns the HLS master playlist file for the given video
        and resolution."""
        path = build_hls_path(movie_id, resolution, 'index.m3u8')
        if not os.path.exists(path):
            raise Http404
        return FileResponse(
            open(path, 'rb'),
            content_type='application/vnd.apple.mpegurl',
        )


class HLSSegmentView(APIView):
    """Serves individual HLS video segments for streaming."""

    def get(self, request, movie_id, resolution, segment):
        """Returns a single HLS video segment for the given video
        and resolution."""
        path = build_hls_path(movie_id, resolution, os.path.basename(segment))
        if not os.path.exists(path):
            raise Http404
        return FileResponse(open(path, 'rb'), content_type='video/MP2T')
