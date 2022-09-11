from django import forms
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User
from ..views import POSTS_ON_SCREEN


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
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.author}):
                'posts/profile.html',
            reverse('posts:post_details', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
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
        """функция проверки контекста постов в тестах"""
        response = self.author_client.get(reverse_path_name)
        post = response.context['page_obj'][0]
        fields = {
            post.text: self.post.text,
            post.author: self.author,
            post.group: self.group,
            post.id: self.post.id,
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_index_context(self):
        """в index передан правильный context"""
        self.post_context_test(reverse('posts:index'))

    def test_group_list_context(self):
        """в group_list передан правильный context"""
        url = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        self.post_context_test(url)
        response = self.author_client.get(url)
        group = response.context['group']
        fields = {
            group.slug: self.group.slug,
            group.title: self.group.title,
            group.description: self.group.description,
            group.id: self.group.id,
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_post_in_right_group(self):
        """пост не публикуется в других группах"""
        response = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.empty_group.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_context(self):
        """в profile передан правильный context"""
        url = reverse('posts:profile', kwargs={'username': self.author})
        self.post_context_test(url)
        response = self.author_client.get(url)
        author = response.context['author']
        self.assertEqual(author, self.author)

    def test_post_in_right_profile(self):
        """пост не публикуется в чужом профайле"""
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_details_context(self):
        """в post_details передан правильный context"""
        response = self.author_client.get(
            reverse('posts:post_details', kwargs={'post_id': self.post.id}))
        post = response.context['post']
        fields = {
            post.text: self.post.text,
            post.author: self.author,
            post.group: self.group,
            post.id: self.post.id,
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
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected_value in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_value)
        self.assertTrue(response.context.get('is_edit'))


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
        posts = [
            Post(
                text=f'test text {num}',
                author=cls.author,
                group=cls.group
            ) for num in range(13)
        ]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_paginator_pages(self):
        """на страницы выводится правильное количество записей"""
        first_page_records = POSTS_ON_SCREEN
        second_page_records = 3
        fields = {
            reverse('posts:index'): first_page_records,
            reverse('posts:index') + '?page=2': second_page_records,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): first_page_records,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ) + '?page=2': second_page_records,
            reverse('posts:profile',
                    kwargs={'username': self.author}
                    ): first_page_records,
            reverse('posts:profile',
                    kwargs={'username': self.author}
                    ) + '?page=2': second_page_records,
        }
        for path, records in fields.items():
            with self.subTest(path=path):
                response = self.author_client.get(path)
                self.assertEqual(len(response.context['page_obj']), records)

    def paginator_create_post(self, path):
        """функция создания нового поста для теста паджинатора"""
        new_post = Post.objects.create(
            text='new post',
            author=self.author,
            group=self.group
        )
        response = self.author_client.get(path)
        post = response.context['page_obj'][0]
        fields = {
            post.text: new_post.text,
            post.author: new_post.author,
            post.group: new_post.group,
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_paginator_create_post(self):
        """При создании новый пост попадает на верх первой страницы"""
        self.paginator_create_post(reverse('posts:index'))
        self.paginator_create_post(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        self.paginator_create_post(reverse(
            'posts:profile',
            kwargs={'username': self.author}))
