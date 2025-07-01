from django.db import models

# Create your models here.
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    participants = models.ManyToManyField('Participant', blank=True)

    def __str__(self):
        return self.name

class Participant(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
