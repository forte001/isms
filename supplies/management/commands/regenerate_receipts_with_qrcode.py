from django.core.management.base import BaseCommand
from supplies.models import Payment, Receipt, Sale
from django.template.loader import render_to_string
from io import BytesIO
import qrcode
from weasyprint import HTML

# Function to generate QR code image
def generate_qr_code(data):
    qr = qrcode.make(data)
    img = BytesIO()
    qr.save(img)
    img.seek(0)
    return img

# Function to generate the PDF receipt
def generate_pdf_receipt(receipt):
    receipt_html = render_to_string('supplies/receipt_template.html', {'receipt': receipt})
    pdf = HTML(string=receipt_html).write_pdf()
    return pdf

class Command(BaseCommand):
    help = 'Regenerate receipts for completed payments'

    def handle(self, *args, **kwargs):
        for payment in Payment.objects.filter(status='completed'):
            sale = payment.sale
            try:
                receipt = Receipt.objects.get(sale=sale)
                self.stdout.write(f"Receipt already exists for Sale {sale.sales_reference}")
                continue
            except Receipt.DoesNotExist:
                receipt = Receipt(
                    sale=sale,
                    transaction_id=payment.transaction_id,
                    amount_paid=payment.amount,
                )
                receipt.save()

                # Generate PDF and save it
                pdf = generate_pdf_receipt(receipt)
                with open(f'receipt_{sale.sales_reference}.pdf', 'wb') as f:
                    f.write(pdf)

                self.stdout.write(f"Generated receipt for Sale {sale.sales_reference}")
