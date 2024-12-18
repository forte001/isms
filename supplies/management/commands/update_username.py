from django.core.management.base import BaseCommand
from supplies.models import Customer

class Command(BaseCommand):
    help = 'Update usernames to customer first names'

    def handle(self, *args, **kwargs):
        customers = Customer.objects.all()
        for customer in customers:
            # Check if the username is None or empty
            if customer.username is None or customer.username == "":
                username = self.generate_unique_username(customer.customer_first_name)
                customer.username = username
                customer.save()  # Save each customer
                self.stdout.write(self.style.SUCCESS(f'Updated username for {customer.username}'))

    def generate_unique_username(self, first_name):
        username = first_name
        counter = 1
        # Ensure the generated username is unique
        while Customer.objects.filter(username=username).exists():
            username = f"{first_name}{counter}"
            counter += 1
        return username


