# Generated by Django 2.2.6 on 2021-05-21 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(help_text='Прокомментируйте запись', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Комментируемая запись'),
        ),
    ]