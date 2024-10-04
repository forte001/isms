from django.urls import path
from .views import *

app_name = 'supplies'

urlpatterns = [
    path("", indexView.as_view(), name="index"),
    path("products/", product_list, name='product_list'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('sales/create/', create_sale, name='create_sale'),
    path('customer/', customer_list, name='customer_list'),
    path('suppliers/', supplier_list, name='supplier_list'),
    path('stock/adjust/', adjust_stock, name='adjust_stock'),
    path('stock/alerts/', low_stock_alerts, name='low_stock_alerts'),


]

