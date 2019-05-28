# Generated by Django 2.1 on 2019-05-28 02:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190528_0157'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='nic_name',
            new_name='nick_name',
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(code='invalid_phone', message='정확한 연락처를 적어주세요.', regex='^0\\d{8,10}$')]),
        ),
    ]
