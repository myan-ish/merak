# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin

# from .models import User
# from .forms import CustomUserCreationForm, CustomUserChangeForm

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = User
#     list_display = ('email', 'is_staff','admin')
#     list_filter = ('email', 'is_staff',)
#     fieldsets = (
#         (None, {'fields': ('email', 'password', 'admin')}),
#         ('Permissions', {'fields': ('is_staff','status')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2', 'is_staff',)}
#          ),
#     )
#     search_fields = ('email',)
#     ordering = ('email',)

# admin.site.register(User, CustomUserAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Attendance, Organization, Team, User
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.widgets import FilteredSelectMultiple

# Create ModelForm based on the Group model.
class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        # Use the pretty 'filter_horizontal widget'.
        widget=FilteredSelectMultiple("users", False),
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields["users"].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data["users"])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("email",)
    list_filter = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password", "status")}),
        ("Basic Info", {"fields": ("first_name", "last_name", "avatar", "address")}),
        ("Organization Info", {"fields": ("organization", "team")}),
        ("Permissions", {"fields": ("is_staff",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


# Unregister the original Group admin.
admin.site.unregister(Group)

# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ["permissions"]


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
admin.site.register(User, CustomUserAdmin)
# admin.site.unregister(Group)
# admin.site.register(Group, CustomGroupAdmin)
# admin.site.register(Group, GroupAdminForm)

admin.site.register(Organization)
admin.site.register(Team)
admin.site.register(Attendance)
