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
        posts_id = []
        for post in Post.objects.all():
            posts_id.append(post.id)

        posts_count = Post.objects.count()
        form_data = {
            'text': 'create post',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.exclude(id__in=posts_id)
        values = last_post.values('text', 'group')[0].values()
        fields = []
        for value in values:
            fields.append(value)

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author}))
        self.assertEqual(fields, ['create post', self.group.id])

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
            edited_post.text: 'post edit',
            edited_post.group: self.group,
        }
        for field, expected_value in values.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, reverse(
            'posts:post_details', kwargs={'post_id': self.post.id}))
