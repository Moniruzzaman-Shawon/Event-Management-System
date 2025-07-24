from django.db import models
from django.conf import settings  

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    image = models.ImageField(
        upload_to='event_images/',
        default='event_images/default.jpg',
        blank=True
    )
    
    # AUTH_USER_MODEL
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="rsvped_events", blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')

    def __str__(self):
        return self.name
