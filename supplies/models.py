from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


    # @admin.display(
    #     boolean=True,
    #     ordering='created_by',
    #     description='Items added by',
    # )

### Product Model
class Product(models.Model):
        product_name = models.CharField(max_length=255)
        description = models.TextField()
        price = models.DecimalField(max_digits=10, decimal_places=2)
        stock_quantity = models.PositiveIntegerField(default=0)
        category = models.ForeignKey('Category', on_delete=models.CASCADE)
        supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)

        def __str__(self):
            return self.product_name
        

### Category Model
class Category(models.Model):
    cat_name = models.CharField(max_length=100)
    cat_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cat_name    
    

### Supplier Model
class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    supplier_email = models.EmailField()
    supplier_phone = models.CharField(max_length=20)

    def __str__(self):
        return self.supplier_name
    

### Customer Model
class Customer(models.Model):
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.customer_first_name} {self.customer_last_name}"
    

### Sale Model
class Sale(models.Model):
    product = models.ForeignKey('supplies.Product', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.quantity} x {self.product.product_name} to {self.customer}"
    

class StockAdjustment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_adjusted = models.IntegerField()
    reason = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.quantity_adjusted} of {self.product.product_name} - {self.reason} on {self.date}"