from django.urls import path
from .views import *
from .views import ProductListView, CreateProductView, ProductDetailView, UpdateProductView, DeleteProductView, ImportProductView, CustomerListView, CustomerDashboardView, DashboardView, DeleteCustomerView, SupplierListView, CreateSupplierView, UpdateSupplierView, DeleteSupplierView, CustomerMultiActionView, PermissionDeniedView, CustomerLoginView, AdjustStockView, CustomerPurchaseDetailsView
# from django.contrib.auth import views as auth_views

app_name = 'supplies'

urlpatterns = [
    path("admin/dashboard/", DashboardView.as_view(), name="admin_dashboard"),
    path("products/", ProductListView.as_view(), name='product_list'),
    path('product/create/', CreateProductView.as_view(), name='create_product'),
    path('product/import/', ImportProductView.as_view(), name='import_products'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/update/<int:product_id>/', UpdateProductView.as_view(), name='update_product'),
    path('product/delete/<int:product_id>/', DeleteProductView.as_view(), name='delete_product'),
    path('sales/create/', create_sale, name='create_sale'),
    path('customer/', CustomerListView.as_view(), name='customer_list'),
    path('customers/access', CustomerMultiActionView.as_view(), name='customer_access'),
    path('customer/delete/<int:customer_id>/', DeleteCustomerView.as_view(), name='delete_customer'),
    path('customer/dashboard', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('customer/purchase_detail', CustomerPurchaseDetailsView.as_view(), name='customer_purchase_details'),
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', CreateSupplierView.as_view(), name='create_supplier'),
    path('supplier/update/<int:supplier_id>', UpdateSupplierView.as_view(), name='update_supplier'),
    path('supplier/delete/<int:supplier_id>/', DeleteSupplierView.as_view(), name='delete_supplier'),
    path('stock/adjust/', AdjustStockView.as_view(), name='adjust_stock'),
    path('stock/alerts/', low_stock_alerts, name='low_stock_alerts'),
    path('customer/logout/', customer_logout_view, name='customer_logout'),
    path('permission-denied/', PermissionDeniedView.as_view(), name='permission_denied'),


]

