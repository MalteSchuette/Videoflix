import os
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video
from .serializers import VideoSerializer


class VideoListView(APIView):
    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


def build_hls_path(movie_id, resolution, filename):
    return os.path.join(settings.MEDIA_ROOT, 'videos', str(movie_id), resolution, filename)


class HLSPlaylistView(APIView):
    def get(self, request, movie_id, resolution):
        path = build_hls_path(movie_id, resolution, 'index.m3u8')
        if not os.path.exists(path):
            raise Http404
        return FileResponse(open(path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    def get(self, request, movie_id, resolution, segment):
        path = build_hls_path(movie_id, resolution, os.path.basename(segment))
        if not os.path.exists(path):
            raise Http404
        return FileResponse(open(path, 'rb'), content_type='video/MP2T')
