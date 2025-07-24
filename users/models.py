from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

def user_profile_path(instance, filename):
    return f"profile_pics/{instance.username}/{filename}"

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Enter a valid phone number in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_path,
        blank=True,
        default='default.png'
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.username
