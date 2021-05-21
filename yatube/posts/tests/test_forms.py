import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user1 = User.objects.create(username="testuser2")
        cls.user1.save()

        cls.group = Group.objects.create(
            title="ж" * 10,
            slug="zh",
            description="описание тестовой группы"
        )

        cls.post1 = Post.objects.create(
            text="Тестовый текст",
            author=cls.user1,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user1 = User.objects.get(username="testuser2")
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            "text": "Новый текст",
            "group": PostCreateFormTests.group.id,
        }
        response = self.authorized_client1.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse("index"))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        new_post_response = self.authorized_client1.get(
            reverse("post",
                    kwargs={
                        "username": PostCreateFormTests.user1.username,
                        "post_id": PostCreateFormTests.post1.id + 1}))
        self.assertEqual(new_post_response.status_code, 200)

    def test_create_new_post_with_image(self):
        """Валидная форма создает запись в Post с изображением."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')

        form_data = {
            "text": "Новый текст 2",
            "group": PostCreateFormTests.group.id,
            "image": uploaded
        }
        response = self.authorized_client1.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse("index"))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        new_post_response = self.authorized_client1.get(
            reverse("post",
                    kwargs={
                        "username": PostCreateFormTests.user1.username,
                        "post_id": PostCreateFormTests.post1.id + 1}))
        self.assertEqual(new_post_response.status_code, 200)

    def test_edit_existing_post(self):
        """Валидная форма редактирует запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()
        # загружаем данные поста, переданные в форму
        response = self.authorized_client1.get(
            reverse("post_edit",
                    kwargs={"username": PostCreateFormTests.user1.username,
                            "post_id": PostCreateFormTests.post1.id})
        )
        post_text = response.context["form"]["text"].value()
        post_group = response.context["form"]["group"].value()
        # Подготавливаем данные для передачи в форму, изменяем текст поста
        form_data = {
            "text": f"{post_text} добавлен текст",
            "group": post_group,
        }
        response = self.authorized_client1.post(
            reverse("post_edit", kwargs={
                    "username": PostCreateFormTests.user1.username,
                    "post_id": PostCreateFormTests.post1.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse("post", kwargs={
                             "username": PostCreateFormTests.user1.username,
                             "post_id": PostCreateFormTests.post1.id})
                             )
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, чтоб сделанная запись изменилась
        PostCreateFormTests.post1.refresh_from_db()
        post_edit_response = PostCreateFormTests.post1
        new_text = post_edit_response.text
        self.assertEqual(new_text, "Тестовый текст добавлен текст")
