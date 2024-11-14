import re

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, ModelForm, IntegerField

from apps.models import User
from apps.models.shops import Order, Stream



class CustomAuthenticationForm(Form):
    phone_number = CharField(max_length=18)
    password = CharField()

    error_messages = {
        "invalid_login": (
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": ("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        return re.sub(r'\D', '', phone_number)[-9:]

    def clean(self):
        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data.get("password")

        if phone_number is not None and password:
            if not User.objects.filter(phone_number=phone_number).exists():
                self.user_cache = User.objects.create_user(**self.cleaned_data)
            else:
                self.user_cache = authenticate(self.request, phone_number=phone_number, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
                return self.cleaned_data

        raise self.get_invalid_login_error()

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"phone_number": 'Phone number'},
        )

class AdminAuthenticationForm(CustomAuthenticationForm):

    def clean(self):
        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data.get("password")

        if phone_number is not None and password:
            if not User.objects.filter(phone_number=phone_number).exists():
                return ValidationError('this user is not found')
            else:
                self.user_cache = authenticate(self.request, phone_number=phone_number, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
                return self.cleaned_data

        raise self.get_invalid_login_error()





class UserChangePasswordModelForm(ModelForm):
    try_new_password = CharField()
    new_password = CharField()

    class Meta:
        model = User
        fields = ('try_new_password', 'new_password', 'password')

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        try_new_password = self.cleaned_data.get('try_new_password')
        if new_password != try_new_password:
            raise ValidationError("didn't match password")
        return new_password

    def clean_password(self):
        new_password = self.cleaned_data.get('new_password')
        password = self.cleaned_data.get('password')
        if not self.instance.check_password(password):
            raise ValidationError('invalid password')
        return make_password(new_password)


class OrderCreateForm(ModelForm):
    class Meta:
        model = Order
        fields = 'name', 'phone_number', 'product', 'stream'

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        phone_number = re.sub(r'\D', '', phone_number)[-9:]
        if len(phone_number) < 9:
            raise ValidationError('Invalid phone number')
        return phone_number


class StreamModelForm(ModelForm):
    class Meta:
        model = Stream
        exclude = 'views_count', 'user'

class OrderUpdateForm(ModelForm):
    class Meta:
        model = Order
        fields = 'count', 'region', 'district', 'delivered_time', 'status', 'comment', 'operator'





