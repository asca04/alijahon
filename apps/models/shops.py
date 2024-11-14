from django.db.models import ForeignKey, CASCADE, ImageField, IntegerField, CharField, OneToOneField, \
    TextChoices, TextField, DateTimeField
from django_ckeditor_5.fields import CKEditor5Field

from apps.models.base import SlugBasedModel, TimeBasedModel


class Category(SlugBasedModel):
    image = ImageField(upload_to='category/%Y/%m/%d')


class Product(SlugBasedModel, TimeBasedModel):
    description = CKEditor5Field('Text', config_name='extends')
    image = ImageField(upload_to='products/%Y/%m/%d')
    price = IntegerField()
    category = ForeignKey('apps.Category', CASCADE, related_name='products')
    bonus = IntegerField(db_default=0)


class Order(TimeBasedModel):
    class ChangeStatus(TextChoices):
        NEW='yangi'
        ARCHIVE = 'arxivlandi'
        DELIVERING = 'yetkazilmoqda'
        DELIVERED = 'yetkazildi'
        BROKEN = 'nosoz_mahsulot'
        RETURNED = 'qaytib_keldi'
        CANCELLED = 'bekor_qilindi'
        WAITING = 'keyin_olinadi'
        READY_TO_DELIVERY = 'dastavkaga_tayyor'
        HOLD='hold'

    name = CharField(max_length=100)
    phone_number = CharField(max_length=18)
    product = ForeignKey('Product', CASCADE, related_name='orders')
    region = ForeignKey('Region', CASCADE, related_name='orders', null=True, blank=True)
    district = ForeignKey("District", CASCADE, related_name='orders', null=True, blank=True)
    count = IntegerField(db_default=1)
    user = ForeignKey('User', CASCADE, related_name='orders', null=True, blank=True)
    stream = ForeignKey('Stream', CASCADE, related_name='orders', null=True, blank=True)
    status = CharField(choices=ChangeStatus.choices, db_default=ChangeStatus.NEW, max_length=50)
    location = TextField(null=True, max_length=200)
    delivered_time = DateTimeField(null=True, blank=True)
    comment = TextField(null=True, blank=True)
    operator = ForeignKey('User', CASCADE, related_name='operator_orders', null=True, blank=True)


    def __str__(self):
        return self.name


class Stream(TimeBasedModel):
    title = CharField(max_length=100)
    discount = IntegerField()
    product = OneToOneField("Product", CASCADE, related_name='streams')
    user = ForeignKey("User", CASCADE, related_name='streams')
    views_count = IntegerField(db_default=0)

    def __str__(self):
        return self.title