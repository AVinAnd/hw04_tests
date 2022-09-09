from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """smoke test"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)


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
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_exist_not_auth_user(self):
        """страницы доступны любому пользователю"""
        field_urls = {
            '/': HTTPStatus.OK.value,
            '/group/test-slug/': HTTPStatus.OK.value,
            '/profile/TestUser/': HTTPStatus.OK.value,
            '/posts/1/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.guest_client.get(field).status_code, expected_value)

    def test_exist_auth_user(self):
        """страницы доступны авторизированному пользователю"""
        field_urls = {
            '/': HTTPStatus.OK.value,
            '/group/test-slug/': HTTPStatus.OK.value,
            '/profile/TestUser/': HTTPStatus.OK.value,
            '/posts/1/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
            '/create/': HTTPStatus.OK.value,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.auth_client.get(field).status_code, expected_value)

    def test_exist_author_user(self):
        """страницы доступны автору поста"""
        field_urls = {
            '/': HTTPStatus.OK.value,
            '/group/test-slug/': HTTPStatus.OK.value,
            '/profile/TestUser/': HTTPStatus.OK.value,
            '/posts/1/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
            '/create/': HTTPStatus.OK.value,
            '/posts/1/edit/': HTTPStatus.OK.value,
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.author_client.get(field).status_code, expected_value)

    def test_redirect_not_auth_user(self):
        """страницы редиректят неавторизированного пользователя """
        field_urls = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/posts/1/',
        }
        for field, expected_value in field_urls.items():
            with self.subTest(field=field):
                self.assertRedirects(
                    self.guest_client.get(field, follow=True), expected_value)

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
