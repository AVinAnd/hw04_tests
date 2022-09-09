from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostsViewsTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('author')
        cls.group = Group.objects.create(
            title='group',
            slug='test-slug',
            description='description'
        )
        cls.post = Post.objects.create(
            text='test text',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_views_templates(self):
        """view функции используют правильные html шаблоны"""
        field_views = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'author'}):
                'posts/profile.html',
            reverse('posts:post_details', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/create_post.html',
        }
        for field, expected_value in field_views.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.author_client.get(field), expected_value)


class PostsViewsContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('user')
        cls.author = User.objects.create_user('author')
        cls.group = Group.objects.create(
            title='group title',
            slug='test-slug',
            description='description'
        )
        cls.post = Post.objects.create(
            text='test post',
            author=cls.author,
            group=cls.group
        )
        cls.empty_group = Group.objects.create(
            title='title',
            slug='empty-slug',
            description='group without posts'
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def post_context_test(self, reverse_path_name):
        response = self.author_client.get(reverse_path_name)
        post = response.context['page_obj'][0]
        fields = {
            post.text: 'test post',
            post.author: self.author,
            post.group: self.group,
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_index_context(self):
        """в index передан правильный context"""
        self.post_context_test(reverse('posts:index'))

    def test_group_list_context(self):
        """в group_list передан правильный context"""
        self.post_context_test(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))

    def test_post_in_right_group(self):
        """пост не публикуется в других группах"""
        response = self.author_client.get(
            reverse('posts:group_list', kwargs={'slug': 'empty-slug'}))
        self.assertEqual(response.context['page_obj'].__len__(), 0)

    def test_profile_context(self):
        """в profile передан правильный context"""
        self.post_context_test(
            reverse('posts:profile', kwargs={'username': 'author'}))

    def test_post_in_right_profile(self):
        """пост не публикуется в чужом профайле"""
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': 'user'}))
        self.assertEqual(response.context['page_obj'].__len__(), 0)

    def test_post_details_context(self):
        """в post_details передан правильный context"""
        response = self.author_client.get(
            reverse('posts:post_details', kwargs={'post_id': 1}))
        post = response.context['post']
        fields = {
            post.text: 'test post',
            post.author: self.author,
            post.group: self.group,
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_post_create_context(self):
        """в post_create передан правильный context"""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected_value in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_value)

    def test_post_edit_context(self):
        """в post_edit передан правильный context"""
        response = self.author_client.get(reverse('posts:post_edit',
                                                  kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected_value in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_value)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('author')
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='description'
        )
        i = 0
        while i != 13:
            Post.objects.create(
                text='text',
                author=cls.author,
                group=cls.group
            )
            i += 1

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_paginator_pages(self):
        """на страницы выводится правильное количество записей"""
        first_page_records = 10
        second_page_records = 3
        fields = {
            reverse('posts:index'): first_page_records,
            reverse('posts:index') + '?page=2': second_page_records,
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}
                    ): first_page_records,
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}
                    ) + '?page=2': second_page_records,
            reverse('posts:profile',
                    kwargs={'username': 'author'}
                    ): first_page_records,
            reverse('posts:profile',
                    kwargs={'username': 'author'}
                    ) + '?page=2': second_page_records,
        }
        for path, records in fields.items():
            with self.subTest(path=path):
                response = self.author_client.get(path)
                self.assertEqual(len(response.context['page_obj']), records)

    def paginator_posts_context(self, path):
        response = self.author_client.get(path)
        post = response.context['page_obj'][0]
        fields = {
            post.text: 'text',
            post.author: self.author,
            post.group: self.group,
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_paginator_posts_context(self):
        """содержимое постов на страницах соответствует ожидаемому"""
        self.paginator_posts_context(reverse('posts:index'))
        self.paginator_posts_context(reverse('posts:index') + '?page=2')
        self.paginator_posts_context(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}))
        self.paginator_posts_context(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}) + '?page=2')
        self.paginator_posts_context(reverse(
            'posts:profile',
            kwargs={'username': 'author'}))
        self.paginator_posts_context(reverse(
            'posts:profile',
            kwargs={'username': 'author'}) + '?page=2')
