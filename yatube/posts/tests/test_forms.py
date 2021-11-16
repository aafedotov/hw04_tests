import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user_author,
            group=cls.group,
            text='Тестовый пост'
        )
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PostTests.user_author
        self.authorized_client = Client()
        self.anonymous_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверяем форму создания поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'image': PostTests.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertTrue(Post.objects.first().image)
        self.assertIsNone(Post.objects.first().group)
        self.assertEqual(Post.objects.first().author, self.user)

    def test_edit_post(self):
        """Проверяем форму редактирования поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст изменение',
        }
        test_post = Post.objects.all().first()
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': test_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': test_post.pk}
            )
        )
        test_post = Post.objects.all().first()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(
            test_post.text,
            form_data['text']
        )
        self.assertIsNone(test_post.group)
        self.assertEqual(Post.objects.first().author, self.user)

    def test_anonymous_create_post(self):
        """Проверяем, что анонимным юзером пост не создается."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.anonymous_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        redirect_url = reverse('users:login') + '?next=' + reverse(
            'posts:post_create'
        )
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Post.objects.count(), post_count)
