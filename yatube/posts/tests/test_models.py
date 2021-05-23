# deals/tests/tests_models.py
from django.test import TestCase
from posts.models import Post, Group
from django.contrib.auth import get_user_model

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД и
        # сохраняем ее в качестве переменной класса
        cls.user = User.objects.create(username="testuser2")
        cls.user.set_password("123456")
        cls.user.save()

        cls.group = Group.objects.create(
            title="ж" * 10,
            description="описание тестовой группы"
        )

        cls.post = Post.objects.create(
            text="Тестовый текст о тестовом тексте",
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст записи",
            "pub_date": "Дата публикации",
            "author": "Автор записи",
            "group": "Группа",
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст вашей записи",
            "pub_date": "Дата, устанавливается автоматически",
            "author": "Укажите автора записи",
            "group": "Укажите группу для размещения записи",
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field_post(self):
        """В поле __str__  объекта post - значение поля post.text ."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="ж" * 10,
            description="описание тестовой группы"
        )

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            "title": "Группа",
            "description": "Описание",
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_group(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            "title": "Название группы",
            "description": "Описание группы",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild_group(self):
        """В поле __str__  объекта task указано значение task.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
