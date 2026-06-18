from rest_framework import serializers
from videos_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializes Video model instances for API responses."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'created_at', 'title', 'description',
            'thumbnail_url', 'category',
        ]

    def get_thumbnail_url(self, obj):
        """Returns the absolute URL of the video thumbnail."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
