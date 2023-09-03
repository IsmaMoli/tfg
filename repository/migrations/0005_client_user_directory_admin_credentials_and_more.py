# Generated by Django 4.2.2 on 2023-08-29 16:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import repository.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('repository', '0004_directory_suggestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='directory',
            name='admin_credentials',
            field=models.ImageField(blank=True, null=True, upload_to=repository.models.credentials_admin_path),
        ),
        migrations.AddField(
            model_name='directory',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='client',
            name='credentials',
            field=models.ImageField(blank=True, null=True, upload_to=repository.models.credentials_directory_path),
        ),
    ]