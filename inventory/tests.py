from asyncio.log import logger
from email import header
from django.urls import reverse
import pytest
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from inventory.models import Order
from inventory.views import AcceptOrderView
from rest_framework.test import APIClient
from django.test.client import Client

from user.models import User

factory = APIRequestFactory()
client = Client()

@pytest.fixture
def admin(db):
    return User.objects.create_user(email="admin@test.com", password="test", status = "Active")

@pytest.fixture
def user_two(db):
    return User.objects.create_user(email="user_two@test.com", password="test", status = "Active")

@pytest.fixture
def staff(db, admin):
    return User.objects.create_user(email="staff@test.com", password="test", status = "Active", admin = admin)

@pytest.fixture
def orderer(db):
    return User.objects.create_user(email="orderer@test.com", password="test", status = "Active")

@pytest.fixture
def order_model(db,orderer, admin):
    return Order.objects.create(ordered_by=orderer, owned_by=admin)

@pytest.fixture
def order_model_with_no_owner(db,orderer, user_two):
    return Order.objects.create(ordered_by=orderer, owned_by=user_two)

@pytest.fixture
def order_model_which_is_assigned_to_another_user(db,orderer, user_two):
    return Order.objects.create(ordered_by=orderer, owned_by=user_two, assigned_to = user_two)

@pytest.fixture
def admin_token(admin):
    response = client.post(
        "/user/auth/login/", {"email": "admin@test.com", "password": "test"}
    )
    return response.data.get("access")

@pytest.fixture
def staff_token(staff):
    response = client.post(
        "/user/auth/login/", {"email": "staff@test.com", "password": "test"}
    )
    return response.data.get("access")

@pytest.fixture
def regular_client(admin_token):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Bearer " + str(admin_token))
    return c


# @pytest.mark.django_db
# def test_login(admin):
#     response = client.post(
#         "/user/auth/login/",{"email": "admin@test.com", "password": "test"}, format="json"
#     )
#     assert response.data == 200
#     assert response.data.get("access") is not None

@pytest.mark.django_db
def test_create_product(regular_client):
    response = regular_client.post(
        "/inventory/product/",
        {
            "name": "test",
            "description": "test product",
            "quantity": 1,
            "price": 1,
            "variant": "test_variant",
            "value": 1,
        },
    )
    assert response.status_code == 201
    assert response.data.get("name") == "test"
    assert response.data.get("description") == "test product"
    assert response.data.get("quantity") == 1
    assert response.data.get("price") == 1
    assert response.data.get("variant").variant_field.name == "test_variant"
    assert response.data.get("variant").variant_field.name == "test_variant"


@pytest.mark.django_db
def test_accept_pending_order_by_owner(admin, order_model, regular_client):
    response = regular_client.get(reverse("accept_pending_order", args =(order_model.uuid,)))
    
    assert response.status_code == 200
    assert response.data.get("status") == "ACCEPTED"
    assert response.data.get("assigned_to") == admin.email

@pytest.mark.django_db
def test_accept_pending_order_by_staff(staff, order_model, regular_client, staff_token):
    regular_client.credentials(HTTP_AUTHORIZATION="Bearer " + str(staff_token))
    response = regular_client.get(reverse("accept_pending_order", args =(order_model.uuid,)))
    
    assert response.status_code == 200
    assert response.data.get("status") == "ACCEPTED"
    assert response.data.get("assigned_to") == staff.email

@pytest.mark.django_db
def test_accept_pending_order_with_invalid_uuid(regular_client):
    response = regular_client.get(reverse("accept_pending_order", args =('invalid_order_uuid',)))
    
    assert response.status_code == 404
    assert response.data.get("detail") == "Order doesn't exists."

@pytest.mark.django_db
def test_accept_pending_order_with_invalid_owner(order_model_with_no_owner, regular_client):
    response = regular_client.get(reverse("accept_pending_order", args =(order_model_with_no_owner.uuid,)))
    
    assert response.status_code == 404
    assert response.data.get("detail") == "Order doesn't exists."

@pytest.mark.django_db
def test_accept_pending_order_with_invalid_assigner(order_model_which_is_assigned_to_another_user, regular_client):
    response = regular_client.get(reverse("accept_pending_order", args =(order_model_which_is_assigned_to_another_user.uuid,)))
    
    assert response.status_code == 404
    assert response.data.get("detail") == "Order doesn't exists."