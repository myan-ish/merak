from django.contrib.auth import get_user_model


User = get_user_model()


def user_authentication_rule(user: User):
    return user and (user.status == "Active" or user.status == "Pending")
