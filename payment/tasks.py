from django.conf import settings
from django.core.mail import send_mail
from orders.models import Order
from io import BytesIO
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import os
import pdfkit
from io import BytesIO
from django.template.loader import get_template
import io
from django.http import HttpResponse
from django.urls import reverse


@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f'My Shop - Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject,
                         message,
                         'admin@myshop.com',
                         [order.email])
    # generate PDF
    html = render_to_string('admin/orders/order/pdf.html', {'order': order})
    pdf_data = pdfkit.from_string(html, False,  options=options, configuration=pdfkit.configuration(
        wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'), css='static/css/pdf.css')
    # attach PDF file
    email.attach(f'order_{order.id}.pdf',
                 BytesIO(pdf_data).getvalue(),
                 'application/pdf')
    # send e-mail
    email.send()
