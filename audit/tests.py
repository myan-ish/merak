import pytest
from audit.models import Ledger, Entry
from user.models import Customer, Organization, User
# @pytest.fixture
# def entry(db):
#     return Entry.objects.create(
#         ledger = Ledger.objects.create(name = "test"),
#         amount = 100,
#         description = "test",
#         type = "Credit",
#         date = "2020-01-01"
#     )

@pytest.fixture
def organization(db):
    return Organization.objects.create(name = "test", owner=User.objects.create_user(email="test@test.com", password="test12345"))

@pytest.fixture
def customer(db, organization):
    return Customer.objects.create(
        name = "test",organization=organization)

@pytest.fixture
def ledger(db, customer):
    return  Ledger.objects.create(name = "test", type="CAPITAL", opening_balance=100, closing_balance=100, related_user=customer)

@pytest.mark.django_db
def test_ledger_transaction_credit(ledger):
    ledger.make_transaction(100, True, "Credit")
    assert ledger.closing_balance == 200

@pytest.mark.django_db
def test_ledger_transaction_debit(ledger):
    ledger.make_transaction(100, False, "Debit")
    assert ledger.closing_balance == 0
