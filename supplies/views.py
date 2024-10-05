# from django.shortcuts import render

from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from .models import  Category,Customer, Sale, StockAdjustment, Supplier, Product
from django.views import generic
from django.shortcuts import render, redirect


class indexView(generic.ListView):
    template_name = "supplies/index.html"
    context_object_name = 'products'


    def get_queryset(self):
        return Product.objects.all()


def product_list(request):
    products = Product.objects.all()
    return render(request, 'supplies/product_list.html', {'products': products})


## Product Detail view
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'supplies/product_detail.html', {'product': product})


def create_sale(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=product_id)
        
        total_price = product.price * quantity
        
        Sale.objects.create(product=product, quantity=quantity, total_price=total_price, customer=request.user)
        
        # Update stock quantity
        product.stock_quantity -= quantity
        product.save()

        return redirect('product_list')
    
    products = Product.objects.all()
    return render(request, 'create_sale.html', {'products': products})


from .models import Customer

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'supplies/customer_list.html', {'customers': customers})

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers})

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

        return redirect('product_list')

    products = Product.objects.all()
    return render(request, 'supplies/adjust_stock.html', {'products': products})

## Low stock alert view
def low_stock_alerts(request):
    threshold = 10  # Define your low stock threshold
    low_stock_products = Product.objects.filter(stock_quantity__lt=threshold)
    return render(request, 'supplies/low_stock_alerts.html', {'low_stock_products': low_stock_products})


