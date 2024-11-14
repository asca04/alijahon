from apps.models import User
from apps.models.managers import AdminManager, OperatorManager, CourierManager, ModeratorManager


class Operatorproxy(User):
    objects = OperatorManager()

    class Meta:
        proxy = True
        verbose_name='Operator'
        verbose_name_plural='Operators'


class Courier(User):
    objects = CourierManager()

    class Meta:
        proxy = True
        verbose_name='Courier'
        verbose_name_plural='Couriers'

class Moderator(User):
    objects = ModeratorManager()

    class Meta:
        proxy = True
        verbose_name='Moderator'
        verbose_name_plural='Moderators'

class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True
        verbose_name='Admin'
        verbose_name_plural='Admins'