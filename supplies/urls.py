from django.urls import path
from .views import *
from .views import ProductListView, CreateProductView, ProductDetailView, UpdateProductView, DeleteProductView, ImportProductView, CustomerListView, CreateCustomerView, LoginView, CustomerDashboardView, DashboardView, DeleteCustomerView, SupplierListView, CreateSupplierView, UpdateSupplierView, DeleteSupplierView


app_name = 'supplies'

urlpatterns = [
    path("", DashboardView.as_view(), name="index"),
    path("products/", ProductListView.as_view(), name='product_list'),
    path('product/create/', CreateProductView.as_view(), name='create_product'),
    path('product/import/', ImportProductView.as_view(), name='import_products'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/update/<int:product_id>/', UpdateProductView.as_view(), name='update_product'),
    path('product/delete/<int:product_id>/', DeleteProductView.as_view(), name='delete_product'),
    path('sales/create/', create_sale, name='create_sale'),
    path('customer/', CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', CreateCustomerView.as_view(), name='customer_access'),
    path('customer/login/', LoginView.as_view(), name='login'),
    path('customer/delete/<int:customer_id>/', DeleteCustomerView.as_view(), name='delete_customer'),
    path('customer/dashboard', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', CreateSupplierView.as_view(), name='create_supplier'),
    path('supplier/update/<int:supplier_id>', UpdateSupplierView.as_view(), name='update_supplier'),
    path('supplier/delete/<int:supplier_id>/', DeleteSupplierView.as_view(), name='delete_supplier'),
    path('stock/adjust/', adjust_stock, name='adjust_stock'),
    path('stock/alerts/', low_stock_alerts, name='low_stock_alerts'),


]

