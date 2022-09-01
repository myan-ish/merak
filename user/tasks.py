import json
import logging
from typing import Tuple
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional, Union
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def smtp(subject, message, recepient):
    send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, [recepient], fail_silently=False
    )