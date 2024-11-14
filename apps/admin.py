import re

from django.contrib import admin
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, CharField
from django.utils.translation import gettext_lazy as _

from apps.models import Region
from apps.models.proxies import Operatorproxy, Courier, Moderator, Admin
from apps.models.shops import Category, Product, Order, Stream
from apps.models.users import User, District


class PhoneWidget(TextInput):
    class Media:
        js = [
            'https://unpkg.com/imask',
            'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
            'https://rawgit.com/RobinHerbots/jquery.inputmask/3.x/dist/jquery.inputmask.bundle.js',
            'apps/main.js',
        ]


class BaseUserAdmin(UserAdmin):
    list_display = 'phone_number', 'first_name', 'last_name', 'telegram_id', 'bio', 'image', 'balance'
    search_fields = 'phone_number',
    ordering = None

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "usable_password", "password1", "password2"),
            },
        ),
    )

    class Media:
        js = [
            'https://unpkg.com/imask',
            'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
            'https://rawgit.com/RobinHerbots/jquery.inputmask/3.x/dist/jquery.inputmask.bundle.js',
            'apps/main.js',
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        return re.sub(r'[^\d]', '', phone_number)[-9:]

    def save_model(self, request, obj, form, change):
        obj.role = self.role
        super().save_model(request, obj, form, change)


@admin.register(Moderator)
class ModeratorAdmin(BaseUserAdmin):
    role = User.Role.MODERATOR
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", 'district')}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Courier)
class CourierAdmin(BaseUserAdmin):
    role = User.Role.COURIER


@admin.register(Operatorproxy)
class OperatorAdmin(BaseUserAdmin):
    role = User.Role.OPERATOR


@admin.register(Admin)
class AdminAdmin(BaseUserAdmin):
    role = User.Role.ADMIN


@admin.register(Region)
class RegionAdmin(ModelAdmin):
    pass


@admin.register(Stream)
class StreamAdmin(ModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    pass


def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    desired_order = ['Users', 'Admins', 'Moderators', 'Operators',
                     'Couriers', 'Categories', 'Products',
                     'Streams', 'Orders', 'Regions', 'Districts']

    # for i in desired_order:
    #     app_list.append(app_dict[i])

    app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
    # print(app_list[0]['models'])
    for app in app_list:
        app["models"].sort(key=lambda x: x['name'])

    return app_list


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    username = CharField(widget=PhoneWidget(attrs={"autofocus": True}))

    def clean_username(self):
        phone = self.cleaned_data.get('username')
        return re.sub(r'[^\d]', '', phone)[-9:]


AdminSite.get_app_list = get_app_list
AdminSite.login_form = CustomAdminAuthenticationForm
