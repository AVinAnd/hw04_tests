from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
CHARS_IN_STR = 15


class Group(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Адрес', unique=True)
    description = models.TextField('Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'


class Post(models.Model):
    text = models.TextField('Текст', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Группа, к которой будет относиться пост'
    )

    def __str__(self):
        return self.text[:CHARS_IN_STR]

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']
