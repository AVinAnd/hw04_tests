from http import HTTPStatus
from django.test import TestCase, Client

from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('TestUser')
        cls.author = User.objects.create_user('Author')
        cls.group = Group.objects.create(
            title='test title',
            slug='test-slug',
            description='test desctiption'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test text'
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_exist_not_auth_user(self):
        """страницы доступны любому пользователю"""
        field_urls = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/TestUser/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.client.get(field).status_code, expected_value)

    def test_exist_auth_user(self):
        """страницы доступны авторизированному пользователю"""
        status_code = self.auth_client.get('/create/').status_code
        self.assertEqual(status_code, HTTPStatus.OK)

    def test_exist_author_user(self):
        """страницы доступны автору поста"""
        status_code = self.author_client.get('/posts/1/edit/').status_code
        self.assertEqual(status_code, HTTPStatus.OK)

    def test_redirect_not_auth_user(self):
        """страницы редиректят неавторизированного пользователя """
        field_urls = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/posts/1/',
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertRedirects(
                    self.client.get(field, follow=True), expected_value)

    def test_redirect_auth_user(self):
        """страница редиректит авторизированного не автора"""
        response = self.auth_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_urls_templates(self):
        """url использует правильный шаблон html"""
        field_urls = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/TestUser/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.author_client.get(field), expected_value)
