from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User


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
        posts_id = Post.objects.values_list('id', flat=True)
        posts_count = len(posts_id)
        form_data = {
            'text': 'create post',
            'group': self.group.id,
            'author': self.author.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.exclude(id__in=list(posts_id))
        self.assertEqual(last_post.count(), 1)
        values = last_post.values('text', 'group', 'author')[0]
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author}))
        self.assertEqual(values, form_data)

    def test_form_post_edit(self):
        """редактируется существующий пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'post edit',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=self.post.id)
        values = {
            edited_post.text: form_data.get('text'),
            edited_post.group: self.group,
        }
        for field, expected_value in values.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, reverse(
            'posts:post_details', kwargs={'post_id': self.post.id}))
