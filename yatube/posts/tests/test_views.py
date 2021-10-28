from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.user_author2 = User.objects.create_user(username='author2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test2',
            description='Тестовое описание 2',
        )
        for i in range(12):
            Post.objects.create(
                author=cls.user_author,
                group=cls.group,
                text=f'Тестовый пост {i}',
            )
        for i in range(12, 15):
            Post.objects.create(
                author=cls.user_author2,
                group=cls.group2,
                text=f'Тестовый пост {i}',
            )

    def setUp(self):
        self.user = PostTemplatesTests.user_author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """
        Проверяем, что во view-функциях используются правильные html-шаблоны.
        """
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'author'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Проверяем контекст и паджинатор главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост 14')
        self.assertEqual(first_object.group, PostTemplatesTests.group2)

    def test_group_page_show_correct_context(self):
        """Проверяем контекст и паджинатор страницы группы."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': 'test'}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        group_objects = response.context['page_obj']
        for post in group_objects:
            self.assertEqual(post.group, self.group)
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': 'test2'}
            )
        )
        group_objects = response.context['page_obj']
        self.assertEqual(group_objects[0].text, 'Тестовый пост 14')

    def test_group_profile_show_correct_context(self):
        """Проверяем контекст и паджинатор страницы профиля."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'author'}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        profile_objects = response.context['page_obj']
        for post in profile_objects:
            self.assertEqual(post.author, self.user)

    def test_group_post_detail_show_correct_context(self):
        """Проверяем контекст страницы поста."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}
            )
        )
        post = response.context['post']
        self.assertEqual(post.id, 1)

    def test_group_post_edit_show_correct_context(self):
        """Проверяем контекст страницы редактирования поста."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}
            )
        )
        form = response.context['form']
        post = response.context['post']
        self.assertEqual(post.id, 1)
        self.assertIsInstance(form.fields.get('text'), forms.fields.CharField)
        self.assertIsInstance(form.fields['group'], forms.fields.ChoiceField)

    def test_group_post_create_show_correct_context(self):
        """Проверяем контекст страницы создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context['form']
        self.assertIsInstance(form.fields.get('text'), forms.fields.CharField)
        self.assertIsInstance(form.fields['group'], forms.fields.ChoiceField)
