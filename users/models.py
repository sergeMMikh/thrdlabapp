from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telephone_number = models.CharField(max_length=20, null=True)

    def __str__(self):
        # return f"{self._meta.fields}"
        return f"{self.first_name}, {self.last_name}, {self.email}"
