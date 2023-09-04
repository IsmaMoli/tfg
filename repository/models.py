import time

from django.db import models
from django.contrib.auth.models import User


def credentials_admin_path(instance, filename):
    return "{0}/credentials_admin/{1}". \
        format(instance.name, filename)


def credentials_directory_path(instance, filename):
    return "{0}/credentials/{1}". \
        format(instance.directory.name, filename)


def client_face_directory_path(instance, filename):
    return "{0}/client_{1}/face_{2}". \
        format(instance.client.directory.name, instance.client.id, filename)


def client_id_directory_path(instance, filename):
    return "{0}/client_{1}/id_{2}". \
        format(instance.client.directory.name, instance.client.id, filename)


def client_failed_directory_path(instance, filename):
    return "{0}/client_{1}/failed_{2}". \
        format(instance.client.directory.name, instance.client.id, filename)


def content_directory_path(instance, filename):
    return "{0}/content/{1}". \
        format(instance.directory.name, filename)


class Directory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    suggestion = models.CharField(max_length=200, blank=True)
    admin_credentials = models.ImageField(upload_to=credentials_admin_path, null=True, blank=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class UniquePass(models.Model):
    dir = models.ForeignKey(Directory, on_delete=models.CASCADE)
    pass_code = models.CharField(max_length=100)

    def __str__(self):
        return "pass of" + self.dir.name + ": " + self.pass_code


class Content(models.Model):
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=content_directory_path, default=None)

    def __str__(self):
        return self.image.name


class Client(models.Model):
    key_words = models.CharField(max_length=200)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    credentials = models.ImageField(upload_to=credentials_directory_path, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.key_words


class LoginAttempt(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    id_frame = models.ImageField(upload_to=client_id_directory_path)
    face_frame = models.ImageField(upload_to=client_face_directory_path)
    failed_frame1 = models.ImageField(upload_to=client_failed_directory_path, blank=True)
    failed_frame2 = models.ImageField(upload_to=client_failed_directory_path, blank=True)
    failed_frame3 = models.ImageField(upload_to=client_failed_directory_path, blank=True)
    failed_frame4 = models.ImageField(upload_to=client_failed_directory_path, blank=True)
    failed_frame5 = models.ImageField(upload_to=client_failed_directory_path, blank=True)

    def __str__(self):
        return ("Attempt of " + self.client.key_words + self.time.strftime(" on %d/%m/%Y at %H:%M:%S"))
