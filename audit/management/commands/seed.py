# Seed 10000 ledgers

from django.core.management.base import BaseCommand
from audit.models import Ledger
from user.models import Customer, Organization, User

class Command(BaseCommand):
    help = 'Seed 10000 ledgers'

    def handle(self, *args, **options):
        organization = Organization.objects.create(name = "test", owner=User.objects.get(email="admin@admin.com"))
        related_user = Customer.objects.create(name="test",organization=organization)
        for i in range(10000):
            Ledger.objects.create(name = "test", type="CAPITAL", opening_balance=100, closing_balance=100, related_user=related_user)
        self.stdout.write(self.style.SUCCESS('Successfully seeded 10000 ledgers'))
