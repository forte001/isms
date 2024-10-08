from django.urls import path
from .views import *
from .views import ProductListView, CreateProductView, ProductDetailView, UpdateProductView, DeleteProductView, ImportProductView


app_name = 'supplies'

urlpatterns = [
    path("", dashboard_view, name="index"),
    path("products/", ProductListView.as_view(), name='product_list'),
    path('product/create/', CreateProductView.as_view(), name='create_product'),
    path('product/import/', ImportProductView.as_view(), name='import_products'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/update/<int:product_id>/', UpdateProductView.as_view(), name='update_product'),
    path('product/delete/<int:product_id>/', DeleteProductView.as_view(), name='delete_product'),
    path('sales/create/', create_sale, name='create_sale'),
    path('customer/', customer_list, name='customer_list'),
    path('customers/create/', create_customer, name='create_customer'), 
    path('suppliers/', supplier_list, name='supplier_list'),
    path('suppliers/create/', create_supplier, name='create_supplier'), 
    path('stock/adjust/', adjust_stock, name='adjust_stock'),
    path('stock/alerts/', low_stock_alerts, name='low_stock_alerts'),


]

