from uuid import uuid4
from supplies.models import Sale, TransactionLog
from django.db import models
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Update sales transaction reference'

    def handle(self, *args, **kwargs):
        # Find duplicates
        duplicates = Sale.objects.values('sales_reference').annotate(count=models.Count('id')).filter(count__gt=1)

        # Update duplicate sales references
        existing_references = set(Sale.objects.values_list('sales_reference', flat=True))
        
        for sale in Sale.objects.filter(sales_reference__in=[d['sales_reference'] for d in duplicates]):
            print("Updating duplicate sales reference...")
            new_reference = uuid4()
            # Ensure the new UUID is unique
            while new_reference in existing_references:
                new_reference = uuid4()
            sale.sales_reference = new_reference
            sale.save()
            existing_references.add(new_reference)  # Add new reference to the set

        # Update sales without references
        sales_without_reference = Sale.objects.filter(sales_reference__isnull=True)
        for sale in sales_without_reference:
            new_reference = uuid4()
            while new_reference in existing_references:
                new_reference = uuid4()
            sale.sales_reference = new_reference
            sale.save()
            existing_references.add(new_reference)  # Add new reference to the set

        # Update Transaction Logs without references
        transactions_without_reference = TransactionLog.objects.filter(transaction_reference__isnull=True)
        for transaction in transactions_without_reference:
            transaction.transaction_reference = uuid4() 
            transaction.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated sales and transaction references.'))

