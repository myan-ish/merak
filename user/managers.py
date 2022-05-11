import logging
import random
import string

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


def get_random_string(length):
    letters = string.printable
    return "".join(random.choice(letters) for _ in range(length))


class CustomAccountManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.create_user(email=email, password=password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.status = "Active"
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("You must provide an email address"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password is None:
            password = get_random_string(32)
            logger.debug("Setting random string as password so user can reset")

        user.set_password(password)
        user.save()
        return user

    def get_or_create_user(self, email, **defaults):
        try:
            user, created = self.get(email=email), False
        except self.model.DoesNotExist:
            user, created = self.create_user(email, **defaults), True
        return user, created
