# Generated by Django 2.1 on 2019-06-02 19:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0005_questioncomment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questioncomment',
            old_name='profile',
            new_name='store_profile',
        ),
        migrations.RemoveField(
            model_name='questioncomment',
            name='author',
        ),
        migrations.AddField(
            model_name='questioncomment',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
