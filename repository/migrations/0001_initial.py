# Generated by Django 4.2.2 on 2023-07-01 09:37

import django.db.models.deletion
from django.db import migrations, models

import repository.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_words', models.CharField(max_length=200)),
                ('credentials', models.ImageField(upload_to=repository.models.credentials_directory_path)),
            ],
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(auto_now=True)),
                ('id_frame', models.ImageField(upload_to=repository.models.client_id_directory_path)),
                ('face_frame', models.ImageField(upload_to=repository.models.client_face_directory_path)),
                ('failed_frame1', models.ImageField(upload_to=repository.models.client_failed_directory_path)),
                ('failed_frame2', models.ImageField(upload_to=repository.models.client_failed_directory_path)),
                ('failed_frame3', models.ImageField(upload_to=repository.models.client_failed_directory_path)),
                ('failed_frame4', models.ImageField(upload_to=repository.models.client_failed_directory_path)),
                ('failed_frame5', models.ImageField(upload_to=repository.models.client_failed_directory_path)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.client')),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=repository.models.content_directory_path)),
                (
                'directory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.directory')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='directory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.directory'),
        ),
    ]
