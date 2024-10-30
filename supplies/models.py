from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid



### Special permission for Admin dashboard
class AdminPermission(models.Model):
    class Meta:
        permissions = [
            ("can_access_admin_dashboard", "Can access the admin dashboard"),
        ]

### Product Model
class Product(models.Model):
        product_name = models.CharField(max_length=255)
        description = models.TextField()
        price = models.DecimalField(max_digits=10, decimal_places=2)
        stock_quantity = models.PositiveIntegerField(default=0)
        category = models.ForeignKey('Category', on_delete=models.SET_NULL,null=True, blank=True)
        supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL,null=True, blank=True)

        class Meta:
            permissions = [
            ("create_product", "Can create product"),
            ("import_product", "Can import product"),
            ("custom_view_product", "Can custom view product"),
            ("custom_update_product", "Can custom update product"),
            ("custom_delete_product", "Can custom delete product"),
        ]

        def __str__(self):
            return self.product_name
        

### Category Model
class Category(models.Model):
    cat_name = models.CharField(max_length=100)
    cat_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cat_name    
    

### Supplier Model
class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    supplier_email = models.EmailField()
    supplier_phone = models.CharField(max_length=20)
    

    class META:
        permissions = [
            ("", "")
        ]

    def __str__(self):
        return self.supplier_name
    

### Customer Model
class Customer(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True)
    customer_first_name = models.CharField(max_length=100, default='customer_first_name')
    customer_last_name = models.CharField(max_length=100, default='customer_last_name')
    customer_email = models.EmailField(unique=True)
    customer_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = [
            ('can_view_profile', 'Can view profile'),
            ('can_edit_profile', 'Can edit profile'),
            ('can_delete_customer', 'Can delete customer')
        ]
    def __str__(self):
        return f"{self.customer_first_name} {self.customer_last_name}"
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    

### Sale Model
class Sale(models.Model):
    sales_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey('supplies.Product', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.quantity} x {self.product.product_name} to {self.customer}"
    


class TransactionLog(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    details = models.TextField()
    customer = models.CharField(max_length=100)
    transaction_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    

    def __str__(self):
        return f"Transaction Log for Sale ID {self.sale.id} at {self.timestamp}"
    

class StockAdjustment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_adjusted = models.IntegerField()
    reason = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.quantity_adjusted} of {self.product.product_name} - {self.reason} on {self.date}"