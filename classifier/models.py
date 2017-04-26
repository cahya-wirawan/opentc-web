from django.db import models


class Classifier(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    is_enabled = models.BooleanField(True)

    def __str__(self):
        return self.name


class Classes(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Classification(models.Model):
    user = models.CharField(max_length=64, null=True)
    data = models.TextField(max_length=1024)
    result = models.CharField(max_length=128, null=True)
    date = models.DateTimeField(null=True)
    ip_address = models.CharField(max_length=128, null=True)