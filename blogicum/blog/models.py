from django.db import models
from django.contrib.auth import get_user_model
from core.models import PublishedModel
from django.utils import timezone
from django.db.models import Count

User = get_user_model()


class PostQuerySet(models.QuerySet):
    def with_comment_count(self):
        return self.annotate(comment_count=Count('comments'))


class Post(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now=False, auto_now_add=False,
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.'))
    image = models.ImageField('Фото', upload_to='profile_images/',
                              null=True, blank=True)
    objects = PostQuerySet.as_manager()
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Category(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.slug


class Location(PublishedModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    first_name = models.CharField(
        max_length=30, verbose_name='Имя', default='Иван')
    last_name = models.CharField(
        max_length=30, verbose_name='Фамилия', default='Иванов')
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    location = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=150, unique=True, default=None)
    email = models.CharField(
        max_length=60,
        default=None,
        verbose_name='Адрес электронной почты'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время регистрации')

    def get_full_name(self):
        return f"{self.first_name or 'Иван'}{self.last_name or 'Иванов'}"

    def __str__(self):
        return self.user.username

    # class Meta:
    #     constraints = (
    #         models.UniqueConstraint(
    #             fields=('first_name', 'last_name', 'username'),
    #             name='Unique person constraint',
    #         ),
    #     )


class Comment(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации комментария')
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.title
