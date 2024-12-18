# from django.shortcuts import render

from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from django.http.response import HttpResponseRedirect
from .models import  Category, Customer, Sale, StockAdjustment, Supplier, Product, Payment, Receipt
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum
from django.views import View
import csv, io, uuid
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.conf import settings
import requests
from django.core.paginator import Paginator
from weasyprint import HTML
from django.template.loader import render_to_string
from datetime import datetime
import qrcode
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


# @method_decorator(login_required, name='dispatch')
# @method_decorator(permission_required('supplies.can_access_admin_dashboard', raise_exception=True), name='dispatch')
class DashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'supplies/admin_dashboard.html'

    def test_func(self):
        return self.request.user.has_perm('supplies.can_access_admin_dashboard')

    def handle_no_permission(self):
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            return redirect('supplies:customer_dashboard')
        else:
            return redirect('supplies:customer_access')

    def get(self, request):
        total_suppliers = Supplier.objects.count()
        total_products = Product.objects.values('product_name').distinct().count()

        # Filter sales for completed transactions only
        completed_sales = Sale.objects.filter(payment__status='completed')

        # Get total purchases (number of completed sales)
        total_sales = completed_sales.aggregate(total=Sum('total_price'))['total'] or 0

        return render(request, self.template_name, {
            'total_suppliers': total_suppliers,
            'total_products': total_products,
            'total_sales': total_sales,
            'recent_transactions': completed_sales.order_by('-date')[:5],
        })

class CreateCategoryView(View):
    template_name = 'supplies/create_category.html'
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        cat_name = request.POST.get('cat_name')
        cat_description = request.POST.get('description')
        


        Category.objects.create(
            cat_name = cat_name,
            cat_description = cat_description,
            created_by = request.user

        )

        return redirect('supplies:category_list')
    


class CategoryListView(View):

    template_name = 'supplies/category_list.html'

    def get(self,request):

        all_categories = Category.objects.all()

        return render(request, self.template_name, {'all_categories': all_categories})
    

class UpdateCategoryView(View):
    template_name = 'supplies/update_category.html'

    def get(self, request, category_id):
       
        category = get_object_or_404(Category, id=category_id)
        return render(request, self.template_name, {'category': category})

    def post(self, request, category_id):
        
        category = get_object_or_404(Category, id=category_id)
        category.cat_name = request.POST.get('cat_name')
        category.cat_description = request.POST.get('cat_description')
        category.created_by = request.user
    
        category.save()

        return redirect('supplies:category_list')

class DeleteCategoryView(View):
    def get(self, request, category_id):
       
        category = get_object_or_404(Category, id=category_id)
        return render(request, 'supplies/delete_category.html', {'category': category})
    def post(self, request, category_id):
         
         category = get_object_or_404(Category, id=category_id)
         category.delete()
         return redirect('supplies:category_list')

    


@method_decorator(login_required, name='dispatch')
class ProductListView(View):
    template_name = 'supplies/product_list.html'

    def get(self, request):
        products = Product.objects.all()
        
         # Check for CSV download request
        if 'download' in request.GET:
            if 'sample' in request.GET:
                return self.download_sample_csv()
            return self.download_csv(products)

        return render(request, self.template_name, {
            'products': products,
            'can_update': request.user.has_perm('supplies.custom_update_product'),
            'can_delete': request.user.has_perm('supplies.custom_delete_product'),
              })

  
  ### Downloads CSV file of products
    def download_csv(self, products):
        # Create an HTTP response with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products_list.csv"'

        # Create a CSV writer
        writer = csv.writer(response)
        writer.writerow(['Product Name', 'Description', 'Price(N)', 'Stock Quantity', 'Category', 'Supplier'])  # Header row
        
        # Write product data
        for product in products:
            writer.writerow([
                product.product_name,
                product.description,
                product.price,
                product.stock_quantity,
                product.category.cat_name if product.category else 'N/A',  # Handle None for category
                product.supplier.supplier_name if product.supplier else 'N/A'  # Handle None for supplier
            ])

        return response
    ### Downloads a sample CSV file with just the header
    def download_sample_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sample_products_list.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product Name', 'Description', 'Price(N)', 'Stock Quantity', 'Category', 'Supplier'])  # Header row

        return response

class CreateProductView(View):
    template_name = 'supplies/create_product.html'

    def get(self, request):
        if not request.user.has_perm('supplies.create_product'):
            return HttpResponse("You do not have permission to create a product.", status=403)
        categories = Category.objects.all()
        suppliers = Supplier.objects.all()
        return render(request, self.template_name, {'categories': categories, 'suppliers': suppliers})

    def post(self, request):
        if not request.user.has_perm('supplies.create_product'):
            return HttpResponse("You do not have permission to create a product.", status=403)
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = float(request.POST.get('price'))
        stock_quantity = int(request.POST.get('stock_quantity'))
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        supplier_id = request.POST.get('supplier_id')
        supplier = Supplier.objects.get(id=supplier_id)

        # Create a new Product object and save it to the database
        Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            category=category,
            supplier=supplier
        )
        
        return redirect('supplies:product_list')
    
    ### imports CSV to create products
class ImportProductView(View):
    template_name = 'supplies/import_product.html'

    def get(self, request):
        if not request.user.has_perm('supplies.import_product'):
            return HttpResponse("You do not have permission to import product.", status=403)
        # Render the import product form
        return render(request, self.template_name)

    def post(self, request):
        if not request.user.has_perm('supplies.import_product'):
            return HttpResponse("You do not have permission to import product.", status=403)
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if csv_file.name.endswith('.csv'):
                # Decode the uploaded CSV file
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)

                next(io_string)  # Skip the header row
                for row in csv.reader(io_string, delimiter=','):
                    # Assign each value from the CSV row to a variable
                    product_name, description, price, stock_quantity, category_name, supplier_name = row

                   # Get category and supplier objects; use None if not found
                    category = Category.objects.filter(cat_name=category_name).first()
                    supplier = Supplier.objects.filter(supplier_name=supplier_name).first()

                    # Create the product
                    Product.objects.create(
                        product_name=product_name,
                        description=description,
                        price=float(price),
                        stock_quantity=int(stock_quantity),
                        category=category,
                        supplier=supplier
                    )

                return redirect('supplies:product_list')
            else:
                return HttpResponse("This is not a CSV file.")
        else:
            return HttpResponse("No CSV file uploaded.")


class ProductDetailView(View):
    template_name = 'supplies/product_detail.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        return render(request, self.template_name, {'product': product})
    
class UpdateProductView(View):
    template_name = 'supplies/update_product.html'

    def get(self, request, product_id):
        if not request.user.has_perm('supplies.update_product'):
            return redirect('supplies:permission_denied')
        product = get_object_or_404(Product, id=product_id)
        categories = Category.objects.all()
        suppliers = Supplier.objects.all()
        return render(request, self.template_name, {'product': product, 'categories': categories, 'suppliers': suppliers})

    def post(self, request, product_id):
        if not request.user.has_perm('supplies.update_product'):
            return redirect('supplies:permission_denied')
        product = get_object_or_404(Product, id=product_id)
        product.product_name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        product.price = float(request.POST.get('price'))
        product.stock_quantity = int(request.POST.get('stock_quantity'))
        product.category = get_object_or_404(Category, id=request.POST.get('category_id'))
        product.supplier = get_object_or_404(Supplier, id=request.POST.get('supplier_id'))
        product.save()

        return redirect('supplies:product_list')

class DeleteProductView(View):
    def get(self, request, product_id):
        if not request.user.has_perm('supplies.update_product'):
            return redirect('supplies:permission_denied')
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'supplies/delete_product.html', {'product': product})
    def post(self, request, product_id):
         if not request.user.has_perm('supplies.update_product'):
            return redirect('supplies:permission_denied')
         product = get_object_or_404(Product, id=product_id)
         product.delete()
         return redirect('supplies:product_list')

def create_sale(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=product_id)

        # Check if there is enough stock
        if product.stock_quantity < quantity:
            messages.error(request, 'Insufficient stock available for this product.')
            return render(request, 'supplies/create_sale.html', {
                'products': Product.objects.all(),
            })

        total_price = product.price * quantity

        # Create the sale
        sale = Sale.objects.create(
            product=product,
            quantity=quantity,
            total_price=total_price,
            customer=request.user
        )

        # Redirect to the payment view with the sales reference
        return redirect('supplies:create_payment', sales_reference=sale.sales_reference)

    products = Product.objects.all()
    return render(request, 'supplies/create_sale.html', {'products': products})


class CreatePaymentView(View):

    def get(self, request, sales_reference):
        sale = get_object_or_404(Sale, sales_reference=sales_reference)
        print("Sales reference for this sale is: "+ str(sales_reference))
        return render(request, 'supplies/payment_form.html', {'sale': sale})

    def post(self, request, sales_reference):
        print("POST request received")
        # Convert sales_reference to string
        sales_reference_str = str(sales_reference)
        # Fetch the sale object using the sales_reference
        try:
            sale = Sale.objects.get(sales_reference=sales_reference_str)
        except Sale.DoesNotExist:
            return JsonResponse({'error': 'Sale not found'}, status=404)
        amount = int(sale.total_price * 100)  # Paystack expects amount in kobo

        # Initialize Paystack payment
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'},
            json={
                'email': request.user.customer_email,
                'amount': amount,
                'metadata': {
                    'sales_reference': sales_reference_str  # To include sales_reference in metadata
                },
                'callback_url': 'https://1b64-102-91-102-29.ngrok-free.app/supplies/payment/callback/',

            }
        )

        response_data = response.json()
        if response_data['status']:
            payment_url = response_data['data']['authorization_url']
            return redirect(payment_url)

        return render(request, 'supplies/error.html', {'message': 'Payment initialization failed.'})


class PaymentCallbackView(View):
    def get(self, request):
        print("Callback view hit!")
        transaction_reference = request.GET.get('reference')
        print("Callback URL accessed with parameters:", request.GET)

        # Verify the transaction with Paystack
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{transaction_reference}',
            headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
        )

        response_data = response.json()

        # Debugging the response data
        print("Response Data: ", response_data)

        # Check if the payment was successful
        if response_data['status'] and response_data['data']['status'] == 'success':
            sales_reference = response_data['data']['metadata']['sales_reference']
            try:
                sale = Sale.objects.get(sales_reference=sales_reference)
            except Sale.DoesNotExist:
                # If Sale doesn't exist, redirect to failure page
                return redirect('supplies:payment_failed')
            
            # Create the receipt if it doesn't exist
            if not Receipt.objects.filter(sale=sale).exists():
                receipt = Receipt.objects.create(
                    sale=sale,
                    transaction_id=transaction_reference,
                    amount_paid=sale.total_price,
                    date_issued=datetime.now()  # Use current time for date_issued
                )

            

            # Create payment record
            Payment.objects.create(
                sale=sale,
                amount=sale.total_price,
                transaction_id=transaction_reference,
                status='completed'
            )

            # Update stock quantity upon successful payment
            product = sale.product
            if product.stock_quantity >= sale.quantity:
                product.stock_quantity -= sale.quantity
                product.save()


            # Redirect to the success page (passing sales_reference for later retrieval)
            return redirect('supplies:payment_success', sales_reference=sale.sales_reference)

        # If payment verification fails, redirect to the failure page
        return redirect('supplies:payment_failed')
    


class PaymentSuccessView(View):
    def get(self, request, sales_reference):
        try:
            sale = Sale.objects.get(sales_reference=sales_reference)
            receipt = Receipt.objects.get(sale=sale)  # Fetch the receipt related to this sale
        except Sale.DoesNotExist:
            return render(request, 'supplies/error.html', {'message': 'Sale not found.'})
        except Receipt.DoesNotExist:
            receipt = None

        # Render success page with sale, product, and receipt information
        return render(request, 'supplies/success.html', {
            'sale': sale,
            'product': sale.product,
            'receipt': receipt,
            'message': 'Payment was successful!'
        })

class PaymentFailedView(View):
    def get(self, request):
        return render(request, 'supplies/error.html', {'message': 'Payment verification failed or transaction was unsuccessful.'})


 
### Generate QR code
def generate_qr_code(data):
    # Generate the QR code from the provided data (like receipt URL or transaction ID)
    qr = qrcode.make(data)
    img = BytesIO()
    qr.save(img)
    img.seek(0)
    return img   

### Generate payment receipt
def generate_pdf_receipt(receipt):
    # Generate the QR code for the receipt URL
    qr_code_url = f'https://1b64-102-91-102-29.ngrok-free.app/supplies/payment/receipt/download/{receipt.sale.sales_reference}'

    qr_code = generate_qr_code(qr_code_url)
    
        # Save the QR code and get the relative path
    qr_filename = f"receipt_{receipt.sale.sales_reference}_qr.png"
    qr_image_path = default_storage.save(qr_filename, ContentFile(qr_code.getvalue()))

    # Get the relative URL of the saved QR code
    qr_image_relative_url = default_storage.url(qr_image_path)

    # Convert it to an absolute URL
    qr_image_url = f"{settings.SITE_URL}{qr_image_relative_url}"

    # Define the template for your receipt
    receipt_html = render_to_string('supplies/receipt_template.html', {'receipt': receipt, 'qr_code_url': qr_image_url})

    # Generate PDF from HTML string
    pdf = HTML(string=receipt_html).write_pdf()

    return pdf

### Download payment receipt
class ReceiptDownloadView(View):
    def get(self, request, sales_reference):
        try:
            sale = Sale.objects.get(sales_reference=sales_reference)
            receipt = Receipt.objects.get(sale=sale)
        except (Sale.DoesNotExist, Receipt.DoesNotExist):
            return render(request, 'supplies/error.html', {'message': 'Receipt not found or payment not completed yet.'})

        # Generate the PDF using the helper function
        pdf = generate_pdf_receipt(receipt)

        # Return the PDF as an HTTP response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{sale.sales_reference}.pdf"'

        return response



class AllSalesView(View):
    template_name = 'supplies/all_sales.html'

    def get(self, request):
        all_sales = Sale.objects.filter(payment__status='completed').order_by('-date')

        # Paginate sales (10 sales per page)
        paginator = Paginator(all_sales, 15)  # Show 15 sales per page
        page_number = request.GET.get('page')  # Get the page number from the request
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {'page_obj': page_obj})

class CustomerListView(PermissionRequiredMixin, View):
    template_name = 'supplies/customer_list.html'
    permission_required = 'supplies:view_customer'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('supplies:customer_dashboard')
        else:
            return redirect('supplies:customer_access')

    def get(self, request):
        customers = Customer.objects.all()
        return render(request, self.template_name, {'customers': customers, 'user': request.user})

class CreateCustomerView( View):
    template_name = 'supplies/customer_access.html'


    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        

        customer_first_name = request.POST.get('customer_first_name')
        username = customer_first_name
        customer_last_name = request.POST.get('customer_last_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        password = request.POST.get('password')
        
         # Check if the email already exists
        if Customer.objects.filter(customer_email=customer_email).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return redirect('supplies:customer_access')
        else:
        # Create a new Customer object and save it to the database
            customer = Customer(
            customer_first_name=customer_first_name,
            username =username,
            customer_last_name=customer_last_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            password = make_password(password)  # Hash the password
        )
            
            customer.save()
            messages.success(request, 'Account created successfully!')
            return redirect('supplies:customer_dashboard')  # Redirect to customer list after saving

class CustomerLoginView(View):

    def post(self, request):
        email = request.POST.get('login_email')
        password = request.POST.get('login_password')

        try:
            customer = Customer.objects.get(customer_email=email)

            # Check if the password is correct
            if customer.check_password(password):
                login(request, customer)  # Log the user in
                request.session['customer_id'] = customer.id  # Store customer ID in session
                return redirect('supplies:customer_dashboard')  # Redirect to the customer Dashboard
            else:
                messages.error(request, 'Invalid email or password.')
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid email or password.')

        return redirect('supplies:customer_access')

@method_decorator(permission_required('supplies.can_delete_customer', raise_exception=True), name='dispatch')   
class DeleteCustomerView(View):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        return render(request, 'supplies/delete_customer.html', {'customer': customer})
    
    def post(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        customer.delete()
        return redirect('supplies:customer_list')
    

class CustomerDashboardView(LoginRequiredMixin, View):
    template_name = 'supplies/customer_dashboard.html'

    def get(self, request):
        customer = request.user

        # Filter sales for completed transactions only
        completed_sales = Sale.objects.filter(customer=customer, payment__status='completed')

        # Get total purchases (number of completed sales)
        total_purchases = completed_sales.count()

        # Get total products (distinct product counts from completed sales)
        total_products = completed_sales.values('product').distinct().count()

        # Get recent purchases
        recent_purchases = completed_sales.order_by('-date')[:5]

        # Calculate total spent on completed transactions only
        total_spent = completed_sales.aggregate(total=Sum('total_price'))['total'] or 0

        return render(request, self.template_name, {
            'total_purchases': total_purchases,
            'recent_purchases': recent_purchases,
            'total_spent': total_spent,
            'total_products': total_products
        })


class CustomerPurchaseDetailsView(View):
    template_name = 'supplies/customer_purchase_details.html'

    @method_decorator(login_required)
    def get(self, request):
        customer = request.user
        
        # Get all sales for the customer
        all_sales = Sale.objects.filter(customer=customer).select_related('product')
       
        # Filter for purchases where payment status is 'completed'
        purchases = all_sales.filter(payment__status='completed')
       
        return render(request, self.template_name, {
            'purchases': purchases
        })

        

# Customer multi action view manages creation of customer account and login 
class CustomerMultiActionView(View):
    template_name = 'supplies/customer_access.html'
    
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if 'create_customer' in request.POST:
            return CreateCustomerView.as_view()(request)

        elif 'login_customer' in request.POST:
            return CustomerLoginView.as_view()(request)

        elif 'customer_pw_reset' in request.POST:
            pass

        return redirect('supplies:customer_access')
        
        
    

class SupplierListView(PermissionRequiredMixin, View):
    template_name = 'supplies/supplier_list.html'
    permission_required = 'supplies.view_supplier'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('supplies:customer_dashboard')
        else:
            return redirect('supplies:customer_access')

    def get(self, request):
        suppliers = Supplier.objects.all()
        return render(request, self.template_name, {'suppliers': suppliers})

class CreateSupplierView(View):
    template_name = 'supplies/create_supplier.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
            supplier_name = request.POST.get('supplier_name')
            supplier_email = request.POST.get('supplier_email')
            supplier_phone = request.POST.get('supplier_phone')

             # Check if the email already exists
            if Supplier.objects.filter(supplier_email=supplier_email).exists():
                messages.error(request, 'Email already exists. Please use a different email.')
                return redirect('supplies:create_supplier')
            else:
        # Create a new Supplier object and save it to the database
                supplier = Supplier( 
                    supplier_name=supplier_name,
                    supplier_email=supplier_email, 
                    supplier_phone=supplier_phone
                    )
        
                supplier.save()
                messages.success(request, 'Account created successfully!')
                return redirect('supplies:supplier_list')  # Redirect to supplier list after saving

class UpdateSupplierView(View):
    template_name = 'supplies/update_supplier.html'

    def get(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, id=supplier_id)
        return render(request, self.template_name, {'supplier':supplier})

    def post(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, id=supplier_id)
        supplier.supplier_name = request.POST.get('supplier_name')
        supplier.supplier_email = request.POST.get('supplier_email')
        supplier.supplier_phone = request.POST.get('supplier_phone')

        supplier.save()
        return redirect('supplies:supplier_list')       

class DeleteSupplierView(View):
    def get(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, id=supplier_id)
        return render(request, 'supplies/delete_supplier.html', {'supplier': supplier})
    
    def post(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, id=supplier_id)
        supplier.delete()
        return redirect('supplies:supplier_list')



class AdjustStockView(View):
    template_name = 'supplies/stock_adjustment.html'

    def get(self, request):
        products = Product.objects.all()
        return render(request, self.template_name, {'products': products} )

    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity_adjusted = int(request.POST.get('quantity_adjusted'))
        reason = request.POST.get('reason')

        product = get_object_or_404(Product, id=product_id)

        # Update stock quantity
        product.stock_quantity += quantity_adjusted
        product.save()

        # Record the stock adjustment
        StockAdjustment.objects.create(product=product, quantity_adjusted=quantity_adjusted, reason=reason)
        
        return redirect('supplies:product_list')

   
## Low stock alert view
def low_stock_alerts(request):
    threshold = 10  # Define your low stock threshold
    low_stock_products = Product.objects.filter(stock_quantity__lt=threshold)
    return render(request, 'supplies/low_stock_alert.html', {'low_stock_products': low_stock_products})


def customer_logout_view(request):
    # Log the user out
    logout(request)
    # Clear the session
    request.session.flush() 
    messages.success(request, "You have been logged out successfully.")
    # Redirect
    return redirect('supplies:customer_access')


class PermissionDeniedView(View):
    template_name = 'supplies/permission_denied.html'

    def get(self, request):
        # message = "You do not have permission to view this page."
       
        return render(request, self.template_name,
        #  {
        #     'message': message,
        #     'referrer_url': referrer_url,
        # }
        )