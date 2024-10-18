from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Product, Category, Supplier, Customer, Sale, StockAdjustment
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages


### Base Test Case available universally to other portion of the test code for use
class BaseTestCase(TestCase):

    """ This portion of code
    make the defined variables available to other portion of 
    the test code for use when extended via the class that wants to use it, thereby avoiding unnecessary repetition
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(cat_name='Electronics', created_by=self.user)
        self.supplier = Supplier.objects.create(supplier_name='Supplier A', supplier_email='contact@supplier.com', supplier_phone='+2347086497348')
        self.customer = Customer.objects.create(customer_first_name='John', customer_last_name='Doe', customer_email='johndoe@company.com', customer_phone='+233807487487')
        self.product = Product.objects.create(product_name='Test Product', description='some product', stock_quantity='4', category=self.category, supplier=self.supplier, price=100.0)
        self.sale = Sale.objects.create(product=self.product, customer=self.customer, quantity=2, total_price='200.00')
        self.adjustment = StockAdjustment.objects.create(product=self.product, quantity_adjusted=5, reason='quantity low')
### Model Tests 
class CategoryModelTest(BaseTestCase):
    def setUp(self):
    # References the BaseTest class and made available for extension and use in other Test classes.
        super().setUp() 
    def test_str(self):
        
        self.assertEqual(str(self.category), 'Electronics')

class SupplierModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_str(self):
        self.assertEqual(str(self.supplier), 'Supplier A')

class CustomerModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_str(self):
        self.assertEqual(str(self.customer), 'John Doe')

class ProductModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        
    def test_str(self):
        self.assertEqual(str(self.product), 'Test Product')

class SaleModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()
   
    def test_str(self):
        self.assertEqual(str(self.sale), f'Sale of {self.sale.quantity} x {self.sale.product.product_name} to {self.customer.customer_first_name} {self.customer.customer_last_name}')

class StockAdjustmentModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_str(self):
        self.assertEqual(str(self.adjustment), f'{self.adjustment.quantity_adjusted} of {self.adjustment.product.product_name} - {self.adjustment.reason} on {self.adjustment.date}')



### View Tests

class DashboardViewTests(TestCase):
    def test_dashboard_view(self):
        response = self.client.get(reverse('supplies:index'))  # Update with the actual name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'supplies/index.html')

class ProductListViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
    

    def test_product_list_view(self):
        response = self.client.get(reverse('supplies:product_list'))  # Update with the actual name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'supplies/product_list.html')
        self.assertContains(response, 'Test Product')

    def test_download_csv(self):
        response = self.client.get(reverse('supplies:product_list') + '?download=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="products_list.csv"')

class CreateProductViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_create_product_view(self):
        response = self.client.get(reverse('supplies:create_product')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'supplies/create_product.html')

    def test_create_product_post(self):
        response = self.client.post(reverse('supplies:create_product'), {
            'product_name': 'New Product',
            'description': 'New Description',
            'price': 20.00,
            'stock_quantity': 50,
            'category_id': self.category.id,
            'supplier_id': self.supplier.id,
        })
        self.assertRedirects(response, reverse('supplies:product_list'))  
        self.assertTrue(Product.objects.filter(product_name='New Product').exists())

class CreateCustomerViewTests(TestCase):

    def setUp(self):
        # Create a customer to test against
        self.existing_customer = Customer.objects.create(
            customer_first_name='John',
            customer_last_name='Doe',
            customer_email='john.doe@example.com',
            customer_phone='1234567890',
            password='hashed_password'  # Hashes password
        )
        self.url = reverse('supplies:customer_dashboard')  # Redirects here

    def test_email_already_exists(self):
        response = self.client.post(self.url, {
            'customer_first_name': 'Jane',
            'customer_last_name': 'Smith',
            'customer_email': 'john.doe@example.com',  # Existing email
            'customer_phone': '0987654321',
            'password': 'newpassword'
        })

        # Check that the response redirects to the same page
        self.assertRedirects(response, self.url)

        # Check for the error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Email already exists. Please use a different email.')

        # Check that the customer count has not increased
        self.assertEqual(Customer.objects.count(), 1)  # Only the existing customer should exist

    def test_create_customer_success(self):
        response = self.client.post(self.url, {
            'customer_first_name': 'Jane',
            'customer_last_name': 'Smith',
            'customer_email': 'jane.smith@example.com',  # New email
            'customer_phone': '0987654321',
            'password': 'newpassword'
        })

        # Check that the response redirects to the customer dashboard
        self.assertRedirects(response, reverse('supplies:customer_dashboard'))

        # Check that the new customer was created
        self.assertEqual(Customer.objects.count(), 2)  # Existing customer + new customer