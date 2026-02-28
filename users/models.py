from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role="REVIEWER"):
        if not email:
            raise ValueError("Email required")

        user = self.model(email=self.normalize_email(email), role=role)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password, role="ADMIN")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("ADMIN", "ADMIN"),
        ("REVIEWER", "REVIEWER"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()