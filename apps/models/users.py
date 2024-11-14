import re

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextChoices, Model, ForeignKey, CASCADE, TextField, IntegerField, ImageField

from apps.models.managers import CustomUserManager


class District(Model):
    name = CharField(max_length=50, unique=True)
    region = ForeignKey('Region', CASCADE, related_name='districts')

    def __str__(self):
        return self.name


class Region(Model):
    name = CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(TextChoices):
        USER = 'user', 'User'
        COURIER = 'courier', 'Courier'
        MODERATOR = 'moderator', 'Moderator'
        ADMIN = 'admin', 'Admin'
        OPERATOR = 'operator', 'Operator'

    username = None
    email = None
    phone_number = CharField(max_length=18, unique=True)
    role = CharField(choices=Role.choices, default=Role.USER, max_length=50)
    district = ForeignKey('District', CASCADE, null=True, related_name="users")
    location = TextField(null=True, blank=True)
    telegram_id = IntegerField(null=True, blank=True)
    bio = TextField(null=True, blank=True)
    image = ImageField(null=True, blank=True)
    balance = IntegerField(db_default=0)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def clean(self):
        self.phone_number = re.sub(r'[^\d]', '', self.phone_number)[-9:]


class Operator(Model):
    user = ForeignKey('User', CASCADE, related_name='operators')
    passport = CharField(max_length=9, null=True)

