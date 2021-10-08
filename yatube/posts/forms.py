"""В этом файле находятся модели основных используемых на сайте форм:
 - создание поста и добавление комментария к посту.
Поля форм взяты из соответствующих моделей файла models.py"""
from django import forms
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    """Настройки формы для создания и редактирования поста
    на основе модели поста"""
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        labels = {"text": _("Текст новой записи")}

    def clean_text(self):
        data = self.cleaned_data["text"]
        if data is None:
            raise forms.ValidationError("Поле 'Текст' должно быть заполнено")
        return data


class CommentForm(forms.ModelForm):
    """Настройки формы для комментариев на основе модели комментариев"""

    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": _("Напишите ваш комментарий")}

    def clean_text(self):
        data = self.cleaned_data["text"]
        if data is None:
            raise forms.ValidationError("Поле 'Текст' должно быть заполнено")
        return data
