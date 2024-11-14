from django.urls import path

from apps.views import (ProductListView, CustomLoginView, CategoryProductListView, AllProductListView,
                        ProductDetailView, ProductMarketListView, ProfileTemplateView, UserUpdateView,
                        LogoutView, OrderDetailView, PasswordUpdateView, StreamListView,
                        StreamDetailView, OrderCreateView, SearchListView, ProductInfoDetailView, OrdersListView,
                        OrderUpdateView, AdminTemplateView, StatistikaListView)

urlpatterns = [

    path('', ProductListView.as_view(), name="product_list"),
    path('search/', SearchListView.as_view(), name='search'),
    path('category/<slug:slug>', CategoryProductListView.as_view(), name='product-filter'),
    path('category/', AllProductListView.as_view(), name='all-products'),
    path('product-detail/<str:slug>', ProductDetailView.as_view(), name='product-detail'),
    path('succes_product/<int:pk>', OrderDetailView.as_view(), name='order-detail'),

    # auth

    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', ProfileTemplateView.as_view(), name='profile'),
    path('profile/settings/', UserUpdateView.as_view(), name='settings'),
    path('profile/logout/', LogoutView.as_view(), name='logout'),
    path('change_password/', PasswordUpdateView.as_view(), name='update-password'),

        #   market

    path('oqim/<int:pk>', StreamDetailView.as_view(), name='stream-detail'),
    path('order_create/', OrderCreateView.as_view(), name='order-create'),

    # admin page

    path('admin_page/market/<slug:slug>', ProductMarketListView.as_view(), name='market'),
    path('admin_page/urls/', StreamListView.as_view(), name='streams'),
    path('admin_page', AdminTemplateView.as_view(), name='for-admins'),
    path('admin_page/product/<int:pk>', ProductInfoDetailView.as_view(), name='product-info'),
    path('admin_page/stats', StatistikaListView.as_view(), name = 'statisika'),

    #     Operator page

    path('operator/<str:status>', OrdersListView.as_view(), name='operator-page'),
    path('operator/order/<int:pk>', OrderUpdateView.as_view(), name='order-update')

]
