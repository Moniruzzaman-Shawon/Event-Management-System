from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

def user_profile_path(instance, filename):
    return f"profile_pics/{instance.username}/{filename}"

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_path, default='default.png', blank=True)

    def __str__(self):
        return self.username
