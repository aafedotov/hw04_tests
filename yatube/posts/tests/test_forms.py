from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


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

    def setUp(self):
        self.user = PostTests.user_author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
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
        self.assertIsNone(Post.objects.first().group)
        self.assertEqual(Post.objects.first().author, self.user)

    def test_edit_post(self):
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
