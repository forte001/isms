# from django.shortcuts import render

from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from .models import  Category, Customer, Sale, StockAdjustment, Supplier, Product
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum
from django.views import View
import csv, io


def dashboard_view(request):
    total_suppliers = Supplier.objects.count()
    total_products = Product.objects.count()
    total_sales = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'supplies/index.html', {
        'total_suppliers': total_suppliers,
        'total_products': total_products,
        'total_sales': total_sales,
        'recent_transactions': Sale.objects.all().order_by('-date')[:5],
    })


class ProductListView(View):
    template_name = 'supplies/product_list.html'

    def get(self, request):
        products = Product.objects.all()
         # Check for CSV download request
        if 'download' in request.GET:
            return self.download_csv(products)
        return render(request, self.template_name, {'products': products})
  
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
                product.category.cat_name,  # Assuming cat_name is the field name for the category
                product.supplier.supplier_name        # Assuming name is the field name for the supplier
            ])

        return response

class CreateProductView(View):
    template_name = 'supplies/create_product.html'

    def get(self, request):
        categories = Category.objects.all()
        suppliers = Supplier.objects.all()
        return render(request, self.template_name, {'categories': categories, 'suppliers': suppliers})

    def post(self, request):
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
        # Render the import product form
        return render(request, self.template_name)

    def post(self, request):
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

                    # Get category and supplier objects
                    category = get_object_or_404(Category, cat_name=category_name)
                    supplier = get_object_or_404(Supplier, supplier_name=supplier_name)

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
        product = get_object_or_404(Product, id=product_id)
        categories = Category.objects.all()
        suppliers = Supplier.objects.all()
        return render(request, self.template_name, {'product': product, 'categories': categories, 'suppliers': suppliers})

    def post(self, request, product_id):
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
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'supplies/delete_product.html', {'product': product})
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('supplies:product_list')

def create_sale(request, ):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=product_id)
        
        total_price = product.price * quantity
        
        Sale.objects.create(product=product, quantity=quantity, total_price=total_price, customer=request.user)
        
        # Update stock quantity
        product.stock_quantity -= quantity
        product.save()

        return redirect('supplies:product_list')
    
    products = Product.objects.all()
    

    return render(request, 'supplies/create_sale.html', {'products': products})



def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'supplies/customer_list.html', {'customers': customers})

def create_customer(request):
    if request.method == 'POST':
        customer_first_name = request.POST.get('customer_first_name')
        customer_last_name = request.POST.get('customer_last_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        
        # Create a new Customer object and save it to the database
        customer = Customer.objects.create(customer_first_name=customer_first_name, customer_last_name=customer_last_name, customer_email=customer_email, customer_phone=customer_phone)
        
        customer.save()
        
        return redirect('supplies:customer_list')  # Redirect to customer list after saving

    return render(request, 'supplies/create_customer.html')  # Render the form for GET requests

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplies/supplier_list.html', {'suppliers': suppliers})


def create_supplier(request):
    if request.method == 'POST':
        supplier_name = request.POST.get('supplier_name')
        supplier_email = request.POST.get('supplier_email')
        supplier_phone = request.POST.get('supplier_phone')
        
        # Create a new Supplier object and save it to the database
        supplier = Supplier.objects.create( supplier_name=supplier_name, supplier_email=supplier_email, supplier_phone=supplier_phone)
        
        supplier.save()
        
        return redirect('supplies:supplier_list')  # Redirect to supplier list after saving

    return render(request, 'supplies/create_supplier.html')  # Render the form for GET requests


def adjust_stock(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity_adjusted = int(request.POST.get('quantity_adjusted'))
        reason = request.POST.get('reason')
        
        product = Product.objects.get(id=product_id)
        
        # Update stock quantity
        product.stock_quantity += quantity_adjusted
        product.save()

        # Record the stock adjustment
        StockAdjustment.objects.create(product=product, quantity_adjusted=quantity_adjusted, reason=reason)

        return redirect('supplies:product_list')

    products = Product.objects.all()
    return render(request, 'supplies/stock_adjustment.html', {'products': products})

## Low stock alert view
def low_stock_alerts(request):
    threshold = 10  # Define your low stock threshold
    low_stock_products = Product.objects.filter(stock_quantity__lt=threshold)
    return render(request, 'supplies/low_stock_alert.html', {'low_stock_products': low_stock_products})


