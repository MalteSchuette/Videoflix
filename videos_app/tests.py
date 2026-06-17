from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from videos_app.models import Video

User = get_user_model()


def create_active_user(email='video_test@example.com', password='Test1234!'):
    """Creates and returns an active test user with the given email
    and password."""
    return User.objects.create_user(
        email=email, password=password, is_active=True
    )


def auth_client(client, user):
    """Sets JWT cookies on the test client so requests are authenticated
    as the given user."""
    refresh = RefreshToken.for_user(user)
    client.cookies['access_token'] = str(refresh.access_token)
    client.cookies['refresh_token'] = str(refresh)
    return client


class VideoListViewTests(APITestCase):
    def setUp(self):
        """Creates an authenticated test user for video list tests."""
        self.user = create_active_user()
        auth_client(self.client, self.user)

    @patch('videos_app.models.django_rq.get_queue')
    def test_video_list_authenticated(self, mock_queue):
        """Checks that an authenticated user can retrieve the video list."""
        mock_queue.return_value.enqueue = MagicMock()
        Video.objects.create(
            title='Test Video',
            category='Action',
            video_file='videos/original/test.mp4',
        )
        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Video')

    def test_video_list_unauthenticated(self):
        """Checks that an unauthenticated request to the video list
        returns 401."""
        self.client.cookies.clear()
        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, 401)


class HLSPlaylistViewTests(APITestCase):
    def setUp(self):
        """Creates an authenticated test user for HLS playlist tests."""
        self.user = create_active_user()
        auth_client(self.client, self.user)

    def test_playlist_not_found(self):
        """Checks that requesting a playlist for a non-existent video
        returns 404."""
        response = self.client.get('/api/video/999/720p/index.m3u8')
        self.assertEqual(response.status_code, 404)

    def test_playlist_unauthenticated(self):
        """Checks that an unauthenticated request to a playlist returns 401."""
        self.client.cookies.clear()
        response = self.client.get('/api/video/1/720p/index.m3u8')
        self.assertEqual(response.status_code, 401)


class HLSSegmentViewTests(APITestCase):
    def setUp(self):
        """Creates an authenticated test user for HLS segment tests."""
        self.user = create_active_user()
        auth_client(self.client, self.user)

    def test_segment_not_found(self):
        """Checks that requesting a segment for a non-existent video
        returns 404."""
        response = self.client.get('/api/video/999/720p/000.ts/')
        self.assertEqual(response.status_code, 404)
