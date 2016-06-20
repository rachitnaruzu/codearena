from __future__ import absolute_import

from celery import shared_task
from django.core.mail import send_mass_mail
from codelabs.config import CODELABS_MAIL_ID

@shared_task
def send_mail_to_many(subject, content, recipientlist):
    datatuple = [(subject, content, CODELABS_MAIL_ID, [email]) for email in recipientlist]
    datatuple = tuple(datatuple)
    send_mass_mail(datatuple)
