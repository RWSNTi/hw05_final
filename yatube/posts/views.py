"""Здесь собраны view-функции, реализующие основную логику проекта.
К страницам с выводом постов подключена пагинация"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    """Отображение постов на главной странице"""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    """Отображение постов в тематических группах"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"groups": group, "page": page})


def profile(request, username):
    """Отображение всех постов автора"""
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    post_count = author_posts.count()
    follow = Follow.objects.filter(user_id=request.user.id
                                   ).filter(author_id=author.id)
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html",
                  {"author": author, "post_count": post_count, "page": page,
                   "follow": follow, }
                  )


def post_view(request, username, post_id):
    """Отображение страницы поста с комментариями к нему"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    author = post.author
    author_posts = author.posts.all()
    post_count = author_posts.count()
    follow = Follow.objects.filter(user_id=request.user.id
                                   ).filter(author_id=author.id).exists()
    form = CommentForm(request.POST or None)
    return render(request, "post.html",
                  {"post": post, "author": author, "post_count": post_count,
                   "comments": comments, "form": form, "follow": follow, }
                  )


@login_required
def add_comment(request, username, post_id):
    """Функция для добавления коментария к посту, используется с декоратором,
    проверяющим аутентификацию пользователя"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def new_post(request):
    """Функция для создания нового поста, используется с декоратором,
    проверяющим аутентификацию пользователя"""
    context = {"header": "Добавить запись", "button": "Добавить"}
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = models.DateTimeField("date published",
                                                 auto_now_add=True
                                                 )
            form.save()
            return redirect("index")

        return render(request, "new.html", {"form": form, "context": context})

    form = PostForm()
    return render(request, "new.html", {"form": form, "context": context})


@login_required
def post_edit(request, username, post_id):
    """Функция для редактирования существующего поста"""
    context = {"header": "Редактировать запись", "button": "Сохранить"}
    if request.user.username != username:
        return redirect("post", username=username, post_id=post_id)
    post = get_object_or_404(Post, id=post_id, author=request.user.id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "new.html", {"form": form, "context": context,
                                        "post": post})


def page_not_found(request, exception):
    """Отображение страницы с ошибкой 404 в стилистике сайта"""
    # подключено в головном url файле папки yatube через handler404
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    """Отображение страницы с ошибкой 500 в стилистике сайта"""
    # подключено в головном url файле папки yatube через handler500
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    """Функция, реализующая просмотр постов всех авторов,
    на которых подписан пользователь"""
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    """Функция, реализующая механизм подписки на автора"""
    get_object_or_404(User, username=username)
    if request.user.username != username:
        Follow.objects.get_or_create(user=request.user,
                                     author=User.objects.get(
                                         username=username))
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    """Функция, реализующая механизм удаления подписки на автора"""
    get_object_or_404(User, username=username)
    Follow.objects.get(
        user=request.user,
        author=User.objects.get(username=username)).delete()
    return redirect("profile", username=username)
