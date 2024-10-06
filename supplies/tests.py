from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from .models import Product, Category, Supplier, Customer, Sale, StockAdjustment


### Model Tests 
class CategoryModelTest(TestCase):
    def setUp(self):
    # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
    def test_str(self):
        category = Category.objects.create(cat_name='Electronics', created_by=self.user)
        self.assertEqual(str(category), 'Electronics')

class SupplierModelTest(TestCase):
    def test_str(self):
        supplier = Supplier.objects.create(supplier_name='Supplier A', supplier_email='contact@supplier.com', supplier_phone='+2347086497348')
        self.assertEqual(str(supplier), 'Supplier A')

class CustomerModelTest(TestCase):
    def test_str(self):
        customer = Customer.objects.create(customer_first_name='John', customer_last_name='Doe', customer_email='johndoe@company.com', customer_phone='+233807487487')
        self.assertEqual(str(customer), 'John'+ ' Doe')

class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(cat_name='Electronics', created_by=self.user)
        self.supplier = Supplier.objects.create(supplier_name='Supplier A', supplier_email='contact@supplier.com', supplier_phone='+2347086497348')
        self.product = Product.objects.create(product_name='Test Product', description='some product', stock_quantity='4', category=self.category, supplier=self.supplier, price=100.0)

    def test_str(self):
        self.assertEqual(str(self.product), 'Test Product')

class SaleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(cat_name='Electronics', created_by=self.user)
        self.supplier = Supplier.objects.create(supplier_name='Supplier A', supplier_email='contact@supplier.com', supplier_phone='+2347086497348')
        self.product = Product.objects.create(product_name='Test Product', category=self.category, supplier=self.supplier, price=100.0)
        self.customer = Customer.objects.create(customer_first_name='John', customer_last_name='Doe', customer_email='johndoe@company.com', customer_phone='+233807487487')
        self.sale = Sale.objects.create(product=self.product, customer=self.customer, quantity=2, total_price='200.00')

    def test_str(self):
        self.assertEqual(str(self.sale), f'Sale of {self.sale.quantity} x {self.sale.product.product_name} to {self.customer.customer_first_name} {self.customer.customer_last_name}')

# class StockAdjustmentModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.date = datetime.now()
#         self.category = Category.objects.create(cat_name='Electronics', created_by=self.user)
#         self.supplier = Supplier.objects.create(supplier_name='Supplier A', supplier_email='contact@supplier.com', supplier_phone='+2347086497348')
#         self.product = Product.objects.create(product_name='Test Product', category=self.category, supplier=self.supplier, price=100.0)
#         self.adjustment = StockAdjustment.objects.create(product=self.product, quantity_adjusted=5, reason='quantity low')

#     def test_str(self):
#         self.assertEqual(str(self.adjustment), f'{self.adjustment.quantity_adjusted} of {self.adjustment.product.product_name} - {self.adjustment.reason} on {self.date}')


