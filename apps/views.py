from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count, Q, F, Case, When, IntegerField
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, CreateView

from apps.forms import (CustomAuthenticationForm, OrderCreateForm, UserChangePasswordModelForm,
                        StreamModelForm, OrderUpdateForm)
from apps.models import Category, Order, Stream, Product, User, Region, District


class ProductListView(ListView):
    queryset = Product.objects.order_by('-created_at').select_related('category')
    template_name = 'apps/products/index.html'
    context_object_name = 'products'
    paginator_class = Paginator
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class CustomLoginView(LoginView):
    template_name = 'apps/auth/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return redirect(reverse_lazy('product_list'))


class CategoryProductListView(ListView):
    queryset = Product.objects.all()
    template_name = "apps/products/category_product.html"
    context_object_name = 'products'
    paginator_class = Paginator
    paginate_by = 3

    def get_queryset(self):
        qs = super().get_queryset()
        if slug := self.kwargs.get('slug'):
            qs = qs.filter(category__slug=slug)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx


class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'apps/products/product_detail.html'
    context_object_name = 'product'


class OrderCreateView(CreateView):
    queryset = Order.objects.all()
    form_class = OrderCreateForm
    template_name = 'apps/products/order_detail.html'

    def get_success_url(self):
        return reverse_lazy('order-detail', kwargs={'pk': self.object.pk})


class ProductMarketListView(LoginRequiredMixin, CreateView, ListView):
    queryset = Product.objects.all()
    template_name = "apps/products/market.html"
    context_object_name = 'products'
    form_class = StreamModelForm
    success_url = reverse_lazy('streams')
    paginate_by = 3

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        qs = super().get_queryset()
        if slug and slug != 'all':
            qs = qs.filter(category__slug=slug)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        stream = form.save(False)
        stream.user = self.request.user
        stream.save()
        return super().form_valid(form)


class AllProductListView(ListView):
    queryset = Product.objects.order_by('-created_at')
    template_name = 'apps/products/all_products.html'
    context_object_name = 'products'
    paginator_class = Paginator
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class ProfileTemplateView(TemplateView):
    template_name = 'apps/auth/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        return redirect(reverse_lazy('login'))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    template_name = 'apps/auth/profile_settings.html'
    fields = 'first_name', 'last_name', 'district', 'location', 'telegram_id', 'bio', 'image',
    success_url = reverse_lazy('settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context

    def get_object(self, queryset=None):
        return self.request.user


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse_lazy('product_list'))


class OrderDetailView(DetailView):
    queryset = Order.objects.all()
    success_url = reverse_lazy('product_list')
    template_name = 'apps/products/order_detail.html'


class PasswordUpdateView(UpdateView):
    queryset = User.objects.all()
    form_class = UserChangePasswordModelForm
    success_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return self.request.user


class StreamListView(LoginRequiredMixin, ListView):
    queryset = Stream.objects.all()
    template_name = 'apps/products/stream.html'
    context_object_name = 'streams'
    paginator_class = Paginator
    paginate_by = 3


class StreamDetailView(LoginRequiredMixin, DetailView):
    queryset = Stream.objects.select_related('product')
    context_object_name = 'stream'
    template_name = 'apps/products/stream_detail.html'
    succes_url = reverse_lazy('')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['price'] = ctx['stream'].product.price - ctx['stream'].discount
        return ctx

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save()
        return obj


class SearchListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/products/index.html'
    context_object_name = 'products'
    paginator_class = Paginator
    paginate_by = 3

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search is not None:
            qs = qs.filter(name__icontains=search)
        return qs


class ProductInfoDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'apps/products/product_info.html'
    context_object_name = 'product'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            all_streams=Count('streams'),
            your_streams=Count('streams', filter=Q(streams__user=self.request.user)),
        )
        return qs


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()
    template_name = 'apps/operators/_orders.html'
    context_object_name = 'orders'
    paginate_by = 2

    def get_queryset(self):
        qs = super().get_queryset()
        dct = {
            'new': Order.ChangeStatus.NEW,
            'ready': Order.ChangeStatus.READY_TO_DELIVERY,
            'delivering': Order.ChangeStatus.DELIVERING,
            'waiting': Order.ChangeStatus.WAITING,
            'archived': Order.ChangeStatus.ARCHIVE,
            'broken': Order.ChangeStatus.BROKEN,
            'delivered': Order.ChangeStatus.DELIVERED,
            'returned': Order.ChangeStatus.RETURNED,
            'cancelled': Order.ChangeStatus.CANCELLED,
            'hold': Order.ChangeStatus.HOLD,
        }
        status = self.kwargs.get('status')

        if status != 'all':
            qs = qs.filter(status=dct[status])
        qs = qs.annotate(price=Case(
            When(stream__isnull=False, then=(F('product__price') - F('stream__discount')) * F('count')),
            default=(F('product__price') * F('count')),
            output_field=IntegerField()
        ))
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx['regions'] = Region.objects.all()
        ctx['districts'] = District.objects.all()
        ctx['products'] = Product.objects.all()
        return ctx

    def get(self, request, *args, **kwargs):
        if self.request.user.role != User.Role.OPERATOR:
            return HttpResponseForbidden()

        return super().get(request, *args, **kwargs)


class OrderUpdateView(UpdateView, LoginRequiredMixin):
    queryset = Order.objects.select_related('stream').select_related('product')
    form_class = OrderUpdateForm
    template_name = 'apps/operators/change_status.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['regions'] = Region.objects.all()
        ctx['districts'] = District.objects.all()
        return ctx

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        if user.role != User.Role.OPERATOR or (obj.operator is not None and obj.operator_id != user.id):
            return HttpResponseForbidden()
        obj = self.get_object()
        obj.operator = self.request.user
        obj.save()
        return super().get(self, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('operator-page', kwargs={'status': 'new'})


class AdminTemplateView(TemplateView, LoginRequiredMixin):
    template_name = 'apps/_admin/for_admin.html'


class StatistikaListView(LoginRequiredMixin, ListView):
    queryset = Stream.objects.select_related('product').prefetch_related('orders')
    template_name = 'apps/products/_statistika.html'
    context_object_name = 'streams'

    def get_queryset(self):
        qs = super().get_queryset()
        dct = {
            'new': Order.ChangeStatus.NEW,
            'ready': Order.ChangeStatus.READY_TO_DELIVERY,
            'delivering': Order.ChangeStatus.DELIVERING,
            'waiting': Order.ChangeStatus.WAITING,
            'archived': Order.ChangeStatus.ARCHIVE,
            'broken': Order.ChangeStatus.BROKEN,
            'delivered': Order.ChangeStatus.DELIVERED,
            'cancelled': Order.ChangeStatus.CANCELLED,
            'hold': Order.ChangeStatus.HOLD,
        }
        return qs.annotate(
            ready_to_delivery_count=Count('orders__id', filter=Q(orders__status=dct['ready'])),
            delivering_count=Count('orders__id', filter=Q(orders__status=dct['delivering'])),
            delivered_count=Count('orders__id', filter=Q(orders__status=dct['delivered'])),
            waiting_count=Count('orders__id', filter=Q(orders__status=dct['waiting'])),
            cancelled_count=Count('orders__id', filter=Q(orders__status=dct['cancelled'])),
            archived_count=Count('orders__id', filter=Q(orders__status=dct['archived'])),
        )
