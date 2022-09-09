from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('author')
        cls.post = Post.objects.create(
            text='test text',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='text'
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_form_post_create(self):
        """создается новый пост"""
        posts_count = Post.objects.count()
        form_data = {'text': 'create post'}
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': 'author'}))
        self.assertTrue(Post.objects.filter(text='create post').exists())

    def test_form_post_edit(self):
        """редактируется существующий пост"""
        post_count = Post.objects.count()
        form_data = {'text': 'post edit'}
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, reverse('posts:post_details', kwargs={'post_id': 1}))
        self.assertTrue(Post.objects.filter(text='post edit').exists())
