import json
import logging
from typing import Tuple
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional, Union
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task
from .tasks import smtp
logger = logging.getLogger(__name__)


def encrypt_data(data: dict, key: bytes) -> str:
    f = Fernet(key)
    json_string = json.dumps(data)
    encrypted_string = f.encrypt(bytes(json_string, encoding="utf-8"))
    return encrypted_string.decode("utf-8")


def decrypt_string(encrypted: Union[str, bytes], key: bytes) -> Optional[dict]:
    f = Fernet(key)
    if not isinstance(encrypted, bytes):
        encrypted = bytes(encrypted, encoding="utf-8")
    try:
        decrypted_string = f.decrypt(encrypted)
        return json.loads(decrypted_string)
    except InvalidToken:
        raise Exception("Invalid Token")


def create_verification_link(user):
    data = {"id": user.pk}
    key = encrypt_data(data, settings.INVITES_KEY)
    verification_url = (
        f"{settings.HOST_URL}/user/auth/verify_email/{key}"
    )
    logger.info(f"Verification URL => {verification_url}&token={key}")
    return verification_url

def password_reset_link(email):
    data = {"email": email}
    key = encrypt_data(data, settings.INVITES_KEY)
    password_reset_email = (
        f"{settings.HOST_URL}/user/auth/verify_reset_password/{key}"
    )
    logger.info(f"Password Reset URL => {password_reset_email}&token={key}")
    return password_reset_email



def send_verification_email(self):
        verification_url =create_verification_link(self)
        smtp(
            subject="Account activation",
            message=f"Please click here to activate your account {verification_url}.",
            recepient=self.email,
        )

@shared_task
def send_password_reset_email(email):
    password_reset_url =password_reset_link(email)
    smtp(
        subject="Password Rest",
        message=f"Please click here to reset your password {password_reset_url}. If this wasn't you, your account is at risk.",
        recepient=email,
    )