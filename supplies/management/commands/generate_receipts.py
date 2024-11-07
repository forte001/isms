from django.core.management.base import BaseCommand
from supplies.models import Payment, Sale, Receipt
from datetime import datetime


class Command(BaseCommand):
    help = 'Generate receipts for previous payments'

    def handle(self, *args, **kwargs):
        # Get all payments
        payments = Payment.objects.all()

        for payment in payments:
            sale = payment.sale

            # Check if a receipt already exists for this sale
            if not Receipt.objects.filter(sale=sale).exists():
                # Create a receipt if one doesn't exist
                receipt = Receipt.objects.create(
                    sale=sale,
                    transaction_id=payment.transaction_id,
                    amount_paid=payment.amount,
                    date_issued=datetime.now()  # Set current time as the receipt issue time
                )

                # Success message
                self.stdout.write(self.style.SUCCESS(f'Receipt generated for Sale {sale.sales_reference}'))

            else:
                # If receipt already exists
                self.stdout.write(self.style.WARNING(f'Receipt already exists for Sale {sale.sales_reference}'))

        self.stdout.write(self.style.SUCCESS('Receipt generation process completed'))
