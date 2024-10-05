from django.test import TestCase
from django.contrib.auth.models import User
from .models import Product, Category, Supplier, Customer, Sale, StockAdjustment


### Model Tests 
class CategoryModelTest(TestCase):
    def test_str(self):
        category = Category.objects.create(cat_name='Electronics')
        self.assertEqual(str(category), 'Electronics')

class SupplierModelTest(TestCase):
    def test_str(self):
        supplier = Supplier.objects.create(supplier_name='Supplier A')
        self.assertEqual(str(supplier), 'Supplier A')

class CustomerModelTest(TestCase):
    def test_str(self):
        customer = Customer.objects.create(customer_first_name='Customer A')
        self.assertEqual(str(customer), 'Customer A')

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(cat_name='Electronics')
        self.supplier = Supplier.objects.create(supplier_name='Supplier A')
        self.product = Product.objects.create(product_name='Test Product', category=self.category, supplier=self.supplier, price=100.0)

    def test_str(self):
        self.assertEqual(str(self.product), 'Test Product')

class SaleModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.supplier = Supplier.objects.create(name='Supplier A')
        self.product = Product.objects.create(name='Test Product', category=self.category, supplier=self.supplier, price=100.0)
        self.customer = Customer.objects.create(name='Customer A')
        self.sale = Sale.objects.create(product=self.product, customer=self.customer, quantity_sold=2)

    def test_str(self):
        self.assertEqual(str(self.sale), f'Sale of {self.sale.quantity_sold} {self.sale.product.name}')

class StockAdjustmentModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.supplier = Supplier.objects.create(name='Supplier A')
        self.product = Product.objects.create(name='Test Product', category=self.category, supplier=self.supplier, price=100.0)
        self.adjustment = StockAdjustment.objects.create(product=self.product, adjustment=5)

    def test_str(self):
        self.assertEqual(str(self.adjustment), f'Stock adjustment for {self.adjustment.product.name}')


