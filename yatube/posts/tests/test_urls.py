from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user1 = User.objects.create(username="testuser2")
        cls.user1.save()

        cls.group = Group.objects.create(
            title="ж" * 3,
            slug="zh" * 3,
            description="описание тестовой группы"
        )

        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user1,
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.get(username="testuser2")
        self.user2 = User.objects.create_user(username="InnaDruz")
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)

    def test_unauth_user_redirects_to_login_after_new(self):
        """Страницы создания поста, комментирования не доступны
         неавторизованному пользователю, делают редирект"""
        pages = {
            "/auth/login/?next=/new/": "/new/",
            f"/auth/login/?next=/{PostURLTests.user1.username}/"
            f"{PostURLTests.post.id}/comment":
            f"/{PostURLTests.user1.username}/"
            f"{PostURLTests.post.id}/comment",
        }
        for redirect_url, url in pages.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_guest_clients_get_pages(self):
        """Проверка доступа у неавторизованных пользователей"""
        pages = {
            "main": "/",
            "profile": f"/{PostURLTests.user1.username}/",
            "group_page": f"/group/{PostURLTests.group.slug}/",
        }
        for page, url in pages.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_logged_clients_get_pages(self):
        """Проверка доступа у авторизованных пользователей"""
        pages = {
            "main": "/",
            "profile": f"/{PostURLTests.user1.username}/",
            "group_page": f"/group/{PostURLTests.group.slug}/",
        }
        for page, url in pages.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    # Проверяем доступность страницы редактирования поста
    #  /<username>/<post_id>/edit/ для разных типов пользователей
    def test_user_post_edit_exists_at_desired_location_unauth_user(self):
        """Страница /<username>/<post_id>/edit/ не доступна
        не залогиненому пользователю."""
        response = self.guest_client.get(
            f"/{PostURLTests.user1.username}/{PostURLTests.post.id}/edit/")
        self.assertEqual(response.status_code, 302)

    def test_user_post_edit_exists_at_desired_location_auth_other_user(self):
        """Страница /<username>/<post_id>/edit/ не доступна
        пользователю - не автору поста."""
        response = self.authorized_client2.get(
            f"/{PostURLTests.user1.username}/{PostURLTests.post.id}/edit/")
        self.assertEqual(response.status_code, 302)

    def test_user_post_edit_exists_at_desired_location_auth(self):
        """Страница /<username>/<post_id>/edit доступна залогиненому
        пользователю."""
        response_auth = self.authorized_client.get(
            f"/{PostURLTests.user1.username}/{PostURLTests.post.id}/edit/")
        self.assertEqual(response_auth.status_code, 200)

    def test_user_gets_404_from_server(self):
        """Пользователь получает ошибку 404, если страница не найдена."""
        response = self.guest_client.get("/page_not_exist/")
        self.assertEqual(response.status_code, 404)

    # проверяем редирект со страницы /<username>/<post_id>/edit/
    # для тех, у кого нет прав доступа к этой странице.
    def test_user_post_edit_redirects_to_login_unauth_user(self):
        """Страница /<username>/<post_id>/edit/ не доступна
        залогиненому пользователю. Перенаправляет на страницу логина"""
        url = (f"/{PostURLTests.user1.username}/"
               f"{PostURLTests.post.id}/edit/")
        response = self.guest_client.get(url)
        self.assertRedirects(
            response, f"/auth/login/?next={url}")

    def test_user_post_edit_redirect_auth_another_user(self):
        """Страница /<username>/<post_id>/edit редиректит на пост
        пользователя не автора поста."""
        url = (f"/{PostURLTests.user1.username}/{PostURLTests.post.id}/")
        response_auth2 = self.authorized_client2.get(f"{url}edit/")
        self.assertRedirects(response_auth2, url)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "index.html": "/",
            "new.html": "/new/",
            "group.html": f"/group/{PostURLTests.group.slug}/",
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
        response2 = self.authorized_client.get(
            f"/{PostURLTests.user1.username}/{PostURLTests.post.id}/edit/")
        self.assertTemplateUsed(response2, "new.html")
