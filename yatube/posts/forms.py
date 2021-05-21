from django import forms
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
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
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": _("Напишите ваш комментарий")}

    def clean_text(self):
        data = self.cleaned_data["text"]
        if data is None:
            raise forms.ValidationError("Поле 'Текст' должно быть заполнено")
        return data
