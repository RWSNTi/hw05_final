import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user1 = User.objects.get(username="testuser2")
        self.user2 = User.objects.create_user(username="InnaDruz")
        self.user3 = User.objects.create_user(username="AnnaGerman")
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client3 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2.force_login(self.user2)
        self.authorized_client3.force_login(self.user3)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            "index.html": reverse("index"),
            "new.html": reverse("new_post"),
            "group.html":
                reverse("group_posts",
                        kwargs={"slug": PostPagesTests.group.slug}),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Проверяем контекст страниц групп и главной"""
        pages = {
            "index.html": reverse("index"),
            "group.html": reverse(
                "group_posts",
                kwargs={"slug": PostPagesTests.group.slug}),
        }
        for template, reverse_name in pages.items():
            with self.subTest(template=template):
                response = self.authorized_client1.get(reverse_name)
                first_object = response.context["page"][0]
                post_text_0 = first_object.text
                post_author_0 = first_object.author.username
                post_group_0 = first_object.group.title
                self.assertEqual(post_text_0, PostPagesTests.post1.text)
                self.assertEqual(post_author_0,
                                 PostPagesTests.post1.author.username)
                self.assertEqual(post_group_0, PostPagesTests.group.title)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client1.get(
            reverse("post_edit",
                    kwargs={"username": PostPagesTests.user1.username,
                            "post_id": PostPagesTests.post1.id})
        )
        post_text = response.context["form"]["text"].value()
        post_group = response.context["form"]["group"].value()
        self.assertEqual(post_text, PostPagesTests.post1.text)
        self.assertEqual(post_group, PostPagesTests.group.id)
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            "text": forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            "group": forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new сформирован с
        правильным контекстом при редактировании."""
        response = self.authorized_client1.get(reverse("new_post"))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            "text": forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            "group": forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context["form"].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client1.get(
            reverse("profile",
                    kwargs={"username": PostPagesTests.user1.username})
        )
        first_object = response.context["page"][0]
        second_object = response.context["author"]
        third_object = response.context["post_count"]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        author = second_object.username
        post_count = third_object
        self.assertEqual(post_text_0, PostPagesTests.post1.text)
        self.assertEqual(post_author_0,
                         PostPagesTests.post1.author.username)
        self.assertEqual(post_group_0, PostPagesTests.group.title)
        self.assertEqual(author, self.user1.username)
        self.assertEqual(post_count, 1)

    def test_profile_post_page_show_correct_context(self):
        """Шаблон поста пользователя сформирован с правильным контекстом."""
        response = self.authorized_client1.get(
            reverse("post",
                    kwargs={"username": PostPagesTests.user1.username,
                            "post_id": PostPagesTests.post1.id})
        )
        first_object = response.context["post"]
        second_object = response.context["author"]
        third_object = response.context["post_count"]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        author = second_object.username
        post_count = third_object
        self.assertEqual(post_text_0, PostPagesTests.post1.text)
        self.assertEqual(post_author_0,
                         PostPagesTests.post1.author.username)
        self.assertEqual(post_group_0, PostPagesTests.group.title)
        self.assertEqual(author, self.user1.username)
        self.assertEqual(post_count, 1)

    def test_post_creation_to_index(self):
        """Проверяем появление нового поста на главной странице."""
        self.authorized_client1.post(
            reverse("new_post"),
            {"text": "Новый автотекст", "group": PostPagesTests.group.id},
            follow=True)
        response2 = self.authorized_client1.get(reverse("index"))
        post_text_added = response2.context["page"][0].text
        self.assertEqual(post_text_added, "Новый автотекст")

    def test_post_creation_to_group(self):
        group2 = Group.objects.create(
            title="222",
            slug="two",
            description="описание тестовой группы2"
        )

        Post.objects.create(
            text="Тестовый текст222",
            author=PostPagesTests.user1,
            group=group2
        )
        """Проверяем появление нового поста на странице группы.
        Проверка отсутствия поста в другой группе"""
        self.authorized_client1.post(
            reverse("new_post"),
            {"text": "Новый автотекст", "group": PostPagesTests.group.id},
            follow=True)
        response2 = self.authorized_client1.get(
            reverse("group_posts",
                    kwargs={"slug": PostPagesTests.group.slug}))
        post_text_added = response2.context["page"][0].text
        self.assertEqual(post_text_added, "Новый автотекст")
        response3 = self.authorized_client1.get(
            reverse("group_posts",
                    kwargs={"slug": "two"}))
        post_text_added2 = response3.context["page"][0].text
        self.assertNotEqual(post_text_added2, "Новый автотекст")

    def test_cache_on_index_page(self):
        """ Проверяем правильность кеширования главной страницы"""
        response1 = self.authorized_client1.get(reverse("index"))
        response1_content = response1.content
        Post.objects.create(
            text="Тестовый текст 222",
            author=PostPagesTests.user1,
            group=PostPagesTests.group
        )
        response2 = self.authorized_client1.get(reverse("index"))
        response2_content = response2.content
        self.assertEqual(response1_content, response2_content)
        cache.clear()
        response3 = self.authorized_client1.get(reverse("index"))
        response3_content = response3.content
        self.assertNotEqual(response1_content, response3_content)

    def test_auth_user_can_sign_up_and_unsign_back(self):
        """Проверяем, что пользователь может подписаться на другого
        пользователя и отписаться обратно"""
        user1_follower_count = PostPagesTests.user1.follower.count()
        self.authorized_client1.get(
            reverse("profile_follow",
                    kwargs={"username": self.user2.username}))
        user1_following_count_2 = PostPagesTests.user1.follower.count()
        self.assertEqual(user1_following_count_2, user1_follower_count + 1)
        self.authorized_client1.get(
            reverse("profile_unfollow",
                    kwargs={"username": self.user2.username}))
        user1_following_count_3 = PostPagesTests.user1.follower.count()
        self.assertEqual(user1_following_count_3, user1_follower_count)

    def test_followers_see_followed_author_s_post(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан на него."""
        Post.objects.create(
            text="Тестовый текст user3", author=self.user3, group=self.group)
        self.authorized_client1.get(
            reverse("profile_follow",
                    kwargs={"username": self.user3.username}))
        self.authorized_client2.get(
            reverse("profile_follow",
                    kwargs={"username": self.user1.username}))
        follow_1_index_user1 = self.authorized_client1.get(
            reverse("follow_index"))
        follow_1_index_user2 = self.authorized_client2.get(
            reverse("follow_index"))
        follow_post1 = follow_1_index_user1.context["page"][0].text
        follow_post_user2_1 = follow_1_index_user2.context["page"][0].text
        new_post_text = "Тестовый новый текст user3"
        Post.objects.create(
            text=new_post_text, author=self.user3, group=self.group)
        follow_2_index_user1 = self.authorized_client1.get(
            reverse("follow_index"))
        follow_2_index_user2 = self.authorized_client2.get(
            reverse("follow_index"))
        follow_post_user2_2 = follow_2_index_user2.context["page"][0].text
        follow_post2 = follow_2_index_user1.context["page"][0].text
        self.assertNotEqual(follow_post2, follow_post1)
        self.assertEqual(follow_post_user2_2, follow_post_user2_1)


class PostImagesTests(TestCase):
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

        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        cls.uploaded = SimpleUploadedFile(
            name="small.gif",
            content=cls.small_gif,
            content_type="image/gif")

        cls.post2 = Post.objects.create(
            text="Тестовый текст 222",
            author=cls.user1,
            group=cls.group,
            image=cls.uploaded
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

    def test_pages_show_correct_image_context(self):
        """Проверяем передачу изображений в контекст страниц"""
        pages = {
            "index.html": reverse("index"),
            "profile.html": reverse(
                "profile",
                kwargs={"username": PostImagesTests.user1.username}),
            "group.html": reverse(
                "group_posts",
                kwargs={"slug": PostImagesTests.group.slug}),
        }
        for template, reverse_name in pages.items():
            with self.subTest(template=template):
                response = self.authorized_client1.get(reverse_name)
                second_object = response.context["page"][0]
                image_post = second_object.image
                self.assertEqual(image_post, PostImagesTests.post2.image)

    def test_post_page_show_correct_image_context(self):
        """Проверяем передачу изображений в контекст страниц"""
        response = self.authorized_client1.get(
            reverse("post",
                    kwargs={"username": PostImagesTests.user1.username,
                            "post_id": PostImagesTests.post2.id}))
        second_object = response.context["post"]
        image_post = second_object.image
        self.assertEqual(image_post, PostImagesTests.post2.image)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user1 = User.objects.create(username="testuser2")
        cls.user1.save()

        cls.group = Group.objects.create(
            title="ж" * 10,
            slug="zh",
            description="описание тестовой группы"
        )
        for i in range(13):
            Post.objects.create(
                text=f"Тестовый текст{i}",
                author=cls.user1,
                group=cls.group
            )

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user1 = User.objects.get(username="testuser2")
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client1.get(reverse("index"))
        posts = response.context.get("page").object_list
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(posts), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client1.get(reverse("index") + "?page=2")
        posts = response.context.get("page").object_list
        self.assertEqual(len(posts), 3)
