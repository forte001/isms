# from django.shortcuts import render

from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from .models import  Category, Customer, Sale, StockAdjustment, Supplier, Product
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Sum



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


def product_list(request):
    products = Product.objects.all()
    return render(request, 'supplies/product_list.html', {'products': products})


## Product Detail view
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'supplies/product_detail.html', {'product': product})


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


