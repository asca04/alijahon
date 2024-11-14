import re

from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password, **extra_fields):

        if not phone_number:
            raise ValueError('The Phone_number must be set')
        phone_number = re.sub(r'\D', '', phone_number)
        if len(phone_number) < 9:
            raise ValueError('invalid phone number')
        user = self.model(phone_number=phone_number[-9:], **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True. ')

        return self.create_user(phone_number, password, **extra_fields)


class AdminManager(CustomUserManager):

    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Role.ADMIN)


class OperatorManager(CustomUserManager):

    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Role.OPERATOR)


class CourierManager(CustomUserManager):

    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Role.COURIER)


class ModeratorManager(CustomUserManager):

    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Role.MODERATOR)
