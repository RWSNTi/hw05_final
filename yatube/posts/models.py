from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        "Текст записи",
        help_text="Введите текст вашей записи"
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
        help_text="Дата, устанавливается автоматически"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор записи",
        related_name="posts",
        help_text="Укажите автора записи"
    )
    group = models.ForeignKey(
        "Group",
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        blank=True, null=True,
        help_text="Укажите группу для размещения записи"
    )
    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True,
        help_text="Добавьте картинку к записи"
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Группа",
        help_text="Название группы"
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(
        max_length=200,
        verbose_name="Описание",
        help_text="Описание группы"
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(
        "Текст записи",
        help_text="Введите текст вашего комментария"
    )
    created = models.DateTimeField(
        "Дата комментария",
        auto_now_add=True,
        help_text="Дата, устанавливается автоматически"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Комментируемая запись",
        related_name="comments",
        help_text="Прокомментируйте запись"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор комментария",
        related_name="comments",
        help_text="Укажите автора комментария"
    )

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписывающийся пользователь",
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписываемся на пользователя",
        related_name="following",
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "author"],
                       name="unique_subscribing",)
                       ]
