# Inventory and Sales Management System

A comprehensive Inventory and Sales Management System built with Django. This system helps manage inventory, track stock levels, manage sales, handle customer accounts, and integrate with PayStack for payment processing. Additionally, it includes features for low stock alerts, bulk import/export of products in CSV format, and detailed statistics on inventory and sales.

## Features

### Inventory Management
- **Add, Update, and Delete Products**: Suppliers can add new products, update details, or remove them from the inventory.
- **Low Stock Alert**: The system automatically alerts when stock is below a predefined threshold, helping manage inventory efficiently.
- **Bulk Import and Export**: Products can be bulk imported or exported using CSV files for quick updates and data analysis.

### Sales Management
- **Sale Transactions**: Products can be sold, and the system tracks sales with all necessary details such as quantity sold, total price, and date.
- **Customer Purchase History**: Customers can view all their past purchases from their account dashboard and download receipt of purchase with QR code embedded.
- **Payment Integration**: Integrated with PayStack for seamless online payments. Sales are completed once payment is verified.
  
### Supplier Management
- **Add Suppliers**: Suppliers can be added to the system, helping track the source of products in your inventory.

### Customer Management
- **Account Creation and Login**: Customers can create an account, log in, and view their purchase history.
  
### Admin Dashboard
- **View Sales and Inventory Stats**: Admins can view sales data, inventory status, and low stock alerts from the admin dashboard for better decision-making.


## Installation

### Prerequisites
- Python 3.x
- Django 3.x+
- PostgreSQL (or any preferred database)
- PayStack Account (for payment integration)

### Steps to Install

1. **Clone the repository:**

   ```bash
   git clone https://github.com/forte001/isms.git

   cd inventory-sales-management


2. **Create Virtual environment**

    ```bash
    python -m venv venv

    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Run Migration**

    ```bash
   python manage.py makemigrations

   python manage.py migrate

4. **Create Super User (Optional)**

    ```bash
    python manage.py createsuperuser



5. **Run development server**

    ```bash
    python manage.py runserver



    Open your browser and go to http://127.0.0.1:8000 to start using the system.

    Access the admin dashboard at http://127.0.0.1:8000/admin with the superuser account.

